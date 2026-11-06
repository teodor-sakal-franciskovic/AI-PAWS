import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.submission import SubmissionStatus
from ..repository.assignment import retrieve_rule_group_percentages
from ..repository.course import instructor_has_access
from ..repository.course import retrieve_by_id as retrieve_course_by_id
from ..repository.group import is_student_assigned_to_instructor
from ..repository.submission import (
    retrieve_rule_evaluations,
    retrieve_submission_file,
    retrieve_submission_in_course,
    update_final_rule_evaluation,
)
from ..repository.submission_mode import (
    retrieve_by_name as retrieve_submission_mode_by_name,
)
from ..repository.user import retrieve_by_id as retrieve_user_by_id
from ..repository.submission_points import retrieve_by_submission_id as retrieve_points
from ..schemas.evaluation import RuleEvaluationRequest
from .points import (
    ai_suggested_ratio,
    assignment_max_points,
    group_shares,
    latest_rule_evaluations,
    points_for,
    refresh_submission_points,
    rule_ratio,
)

PDF_MIME_TYPE = "application/pdf"
FULFILLMENT_SCALE = [
    {"value": 0, "code": "NOT_FULFILLED"},
    {"value": 1, "code": "PARTIALLY_FULFILLED"},
    {"value": 2, "code": "FULFILLED"},
]


def _result(ratio: float | None, achieved_points: float | None) -> dict | None:
    if ratio is None:
        return None
    return {
        "fulfillment_ratio": round(ratio, 4),
        "achieved_points": achieved_points,
    }


def _access_denied() -> ApiError:
    return ApiError(
        403,
        "SUBMISSION_EVALUATION_ACCESS_DENIED",
        "You do not have access to this submission's evaluation.",
    )


def _load_evaluation_context(
    db: Session, course_id: int, submission_id: int, instructor_id: int
):
    course = retrieve_course_by_id(db, course_id)
    if not course:
        raise ApiError(404, "COURSE_NOT_FOUND", "Course not found.")

    found = retrieve_submission_in_course(db, submission_id, course_id)
    evaluative_mode = retrieve_submission_mode_by_name(db, "Evaluative mode")
    if not found or found.Assignment.submission_mode_id != evaluative_mode.id:
        raise ApiError(404, "SUBMISSION_NOT_FOUND", "Submission not found in this course.")
    submission, assignment, has_file = found

    if not instructor_has_access(db, course, instructor_id) or not (
        is_student_assigned_to_instructor(db, course_id, submission.user_id, instructor_id)
    ):
        raise _access_denied()
    return course, submission, assignment, has_file


def _file_name(file_name: str | None, student_index: str | None, assignment_name: str) -> str:
    if file_name:
        return file_name
    slug = re.sub(r"[^\w]+", "-", assignment_name.lower()).strip("-")
    return f"{student_index}-{slug}.pdf" if student_index else f"{slug}.pdf"


def _evaluation(db: Session, submission, rules: list, percentages, points) -> dict:
    ai_ratio = ai_suggested_ratio(rules, percentages)
    final_ratio = submission.fulfillment_ratio if submission.graded else None
    grader = retrieve_user_by_id(db, submission.graded_by) if submission.graded_by else None
    return {
        "grading_status": "GRADED" if submission.graded else "NOT_GRADED",
        "ai_suggested_result": _result(
            ai_ratio, points.ai_suggested_points if points else None
        ),
        "final_result": _result(final_ratio, points.final_points if points else None),
        "graded_at": submission.graded_at,
        "graded_by": {
            "instructor_id": grader.id,
            "name": grader.name,
            "surname": grader.surname,
        }
        if grader
        else None,
    }


def _rule_groups(rules: list, percentages, max_points) -> list[dict]:
    groups: dict[int | None, dict] = {}
    for rule in rules:
        groups.setdefault(
            rule.rule_group_id, {"name": rule.rule_group_name, "rules": []}
        )["rules"].append(rule)
    shares = group_shares(list(groups), percentages)

    result = []
    for position, (group_id, group) in enumerate(groups.items(), start=1):
        group_max = round(max_points * shares[group_id], 2) if max_points is not None else None
        ai_values = [r.initial_fulfillment_value for r in group["rules"] if r.initial_fulfillment_value is not None]
        final_values = [r.final_fulfillment_value for r in group["rules"] if r.final_fulfillment_value is not None]
        result.append(
            {
                "id": group_id,
                "name": group["name"],
                "position": position,
                "percentage_of_points_in_assignment": percentages.get(group_id),
                "summary": {
                    "rules_count": len(group["rules"]),
                    "finalized_rules_count": len(final_values),
                    "max_points": group_max,
                    "ai_suggested_achieved_points": points_for(rule_ratio(ai_values), group_max)
                    if ai_values
                    else None,
                    "final_achieved_points": points_for(rule_ratio(final_values), group_max)
                    if final_values
                    else None,
                },
                "rules": [
                    {
                        "id": rule.rule_id,
                        "position": rule_position,
                        "name": rule.rule_name,
                        "description": rule.rule_description,
                        "generated_description": rule.rule_generated_description,
                        "evaluation": {
                            "ai_suggestion": {
                                "feedback_text": rule.feedback_text,
                                "fulfillment_value": rule.initial_fulfillment_value,
                            },
                            "final": {
                                "feedback_text": rule.final_feedback_text,
                                "fulfillment_value": rule.final_fulfillment_value,
                            }
                            if rule.final_fulfillment_value is not None
                            else None,
                        },
                    }
                    for rule_position, rule in enumerate(group["rules"], start=1)
                ],
            }
        )
    return result


def get_submission_evaluation(
    db: Session, course_id: int, submission_id: int, instructor_id: int
) -> dict:
    course, submission, assignment, has_file = _load_evaluation_context(
        db, course_id, submission_id, instructor_id
    )
    student = retrieve_user_by_id(db, submission.user_id)
    points = retrieve_points(db, submission.id)
    max_points = (
        points.max_points
        if points
        else assignment_max_points(
            course.max_amount_of_points, assignment.percentage_of_points_in_course
        )
    )
    rules = latest_rule_evaluations(retrieve_rule_evaluations(db, submission.id))
    percentages = retrieve_rule_group_percentages(db, assignment.id)
    completed = submission.status == SubmissionStatus.COMPLETED.value

    return {
        "course": {"id": course.id, "name": course.name},
        "student": {
            "student_id": student.id,
            "student_index": student.index,
            "name": student.name,
            "surname": student.surname,
        },
        "assignment": {
            "id": assignment.id,
            "name": assignment.name,
            "start_date": assignment.start_date,
            "end_date": assignment.end_date,
            "max_points": max_points,
        },
        "submission": {
            "id": submission.id,
            "status": submission.status,
            "submitted_at": submission.submitted_at,
            "file": {
                "name": _file_name(submission.file_name, student.index, assignment.name),
                "mime_type": PDF_MIME_TYPE,
                "download_url": f"/submissions/{submission.id}/file",
            }
            if has_file
            else None,
        },
        "evaluation": _evaluation(db, submission, rules, percentages, points),
        "fulfillment_scale": FULFILLMENT_SCALE,
        "rule_groups": _rule_groups(rules, percentages, max_points),
        "permissions": {
            "can_view": True,
            "can_grade": completed and not submission.graded,
            "can_edit_grade": completed and bool(submission.graded),
        },
    }


def _validate_rule_evaluations(
    rule_evaluations: list[RuleEvaluationRequest], rules_by_id: dict
) -> None:
    ids = [evaluation.rule_id for evaluation in rule_evaluations]
    duplicates = sorted({rule_id for rule_id in ids if ids.count(rule_id) > 1})
    unknown = sorted(set(ids) - set(rules_by_id))
    missing = sorted(set(rules_by_id) - set(ids))
    if duplicates or unknown or missing:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            "rule_evaluations must contain every rule of this submission exactly once.",
            data={
                "duplicate_rule_ids": duplicates,
                "unknown_rule_ids": unknown,
                "missing_rule_ids": missing,
            },
        )


def save_final_evaluation(
    db: Session,
    course_id: int,
    submission_id: int,
    instructor_id: int,
    rule_evaluations: list[RuleEvaluationRequest],
    is_update: bool,
) -> dict:
    course, submission, assignment, _ = _load_evaluation_context(
        db, course_id, submission_id, instructor_id
    )
    if submission.status != SubmissionStatus.COMPLETED.value:
        raise ApiError(
            409,
            "SUBMISSION_NOT_READY_FOR_GRADING",
            "Only completed submissions can be graded.",
        )
    if is_update and not submission.graded:
        raise ApiError(
            404,
            "FINAL_EVALUATION_NOT_FOUND",
            "This submission hasn't been graded yet.",
        )
    if not is_update and submission.graded:
        raise ApiError(
            409,
            "EVALUATION_ALREADY_GRADED",
            "This submission has already been graded.",
        )

    rules = latest_rule_evaluations(retrieve_rule_evaluations(db, submission.id))
    rules_by_id = {rule.rule_id: rule for rule in rules}
    _validate_rule_evaluations(rule_evaluations, rules_by_id)

    for evaluation in rule_evaluations:
        rule = rules_by_id[evaluation.rule_id]
        update_final_rule_evaluation(
            db,
            rule.fulfillment_id,
            rule.feedback_id,
            evaluation.final_fulfillment_value,
            evaluation.final_feedback_text,
        )

    submission.graded = True
    submission.graded_by = instructor_id
    submission.graded_at = datetime.now(timezone.utc).replace(tzinfo=None)
    points = refresh_submission_points(db, submission)
    db.commit()
    db.refresh(submission)
    db.refresh(points)

    percentages = retrieve_rule_group_percentages(db, assignment.id)
    return _evaluation(db, submission, rules, percentages, points)


def get_submission_file(db: Session, submission_id: int, instructor_id: int):
    row = retrieve_submission_file(db, submission_id)
    if not row:
        raise ApiError(404, "SUBMISSION_NOT_FOUND", "Submission not found.")
    course = retrieve_course_by_id(db, row.course_id)
    if not course:
        raise ApiError(404, "SUBMISSION_NOT_FOUND", "Submission not found.")
    if not instructor_has_access(db, course, instructor_id) or not (
        is_student_assigned_to_instructor(db, course.id, row.user_id, instructor_id)
    ):
        raise ApiError(
            403,
            "SUBMISSION_ACCESS_DENIED",
            "You do not have access to this submission.",
        )
    if row.file_bytes is None:
        raise ApiError(404, "SUBMISSION_FILE_NOT_FOUND", "This submission has no file.")
    return row.file_bytes, _file_name(row.file_name, row.student_index, row.assignment_name)
