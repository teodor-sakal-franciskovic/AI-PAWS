from sqlalchemy.orm import Session

from ..models.course import Course
from ..models.submission import Submission
from ..models.submission_points import SubmissionPoints
from ..models.user_course_points import UserCoursePoints
from ..repository.assignment import retrieve_by_id as retrieve_assignment_by_id
from ..repository.assignment import retrieve_rule_group_percentages
from ..repository.submission import (
    retrieve_completed_submissions_in_course,
    retrieve_rule_evaluations,
)
from ..repository.submission_mode import (
    retrieve_by_name as retrieve_submission_mode_by_name,
)
from ..repository.submission_points import (
    retrieve_completed_points_for_student,
    save_submission_points,
)
from ..repository.user_course_points import save_user_course_points

MAX_RULE_GRADE = 2


def assignment_max_points(
    course_max_points: float | None, percentage_of_points_in_course: float | None
) -> float | None:
    if course_max_points is None or percentage_of_points_in_course is None:
        return None
    return round(course_max_points * percentage_of_points_in_course / 100, 2)


def rule_ratio(values: list[int]) -> float:
    return sum(values) / (MAX_RULE_GRADE * len(values))


def group_shares(
    group_ids: list[int | None], percentages: dict[int, float | None]
) -> dict[int | None, float]:
    weights = {group: percentages.get(group) for group in group_ids}
    if not weights:
        return {}
    if any(weight is None for weight in weights.values()) or sum(weights.values()) <= 0:
        weights = {group: 1.0 for group in group_ids}
    total_weight = sum(weights.values())
    return {group: weight / total_weight for group, weight in weights.items()}


def calculate_weighted_score(
    values: list[tuple[int | None, int]],
    percentages: dict[int, float | None],
) -> float:
    values_by_group: dict[int | None, list[int]] = {}
    for rule_group_id, value in values:
        values_by_group.setdefault(rule_group_id, []).append(value)
    shares = group_shares(list(values_by_group), percentages)
    return sum(
        shares[group] * rule_ratio(group_values)
        for group, group_values in values_by_group.items()
    )


def points_for(ratio: float | None, max_points: float | None) -> float | None:
    if ratio is None or max_points is None:
        return None
    return round(ratio * max_points, 2)


def latest_rule_evaluations(rows) -> list:
    latest_by_rule = {}
    for row in rows:
        latest_by_rule[row.rule_id] = row
    return list(latest_by_rule.values())


def ai_suggested_ratio(rules: list, percentages) -> float | None:
    values = [
        (rule.rule_group_id, rule.initial_fulfillment_value)
        for rule in rules
        if rule.initial_fulfillment_value is not None
    ]
    return calculate_weighted_score(values, percentages) if values else None


def _final_ratio(submission: Submission, rules: list, percentages) -> float | None:
    values = [(rule.rule_group_id, rule.final_fulfillment_value) for rule in rules]
    if not values or any(value is None for _, value in values):
        return submission.fulfillment_ratio
    return calculate_weighted_score(values, percentages)


def _save_points_for_submission(
    db: Session, submission: Submission
) -> tuple[SubmissionPoints, int | None]:
    assignment = retrieve_assignment_by_id(db, submission.assignment_id)
    course = db.get(Course, assignment.course_id) if assignment.course_id else None
    max_points = assignment_max_points(
        course.max_amount_of_points if course else None,
        assignment.percentage_of_points_in_course,
    )
    rules = latest_rule_evaluations(retrieve_rule_evaluations(db, submission.id))
    percentages = retrieve_rule_group_percentages(db, assignment.id)

    final_ratio = None
    if submission.graded:
        final_ratio = _final_ratio(submission, rules, percentages)
        submission.fulfillment_ratio = final_ratio
    points = save_submission_points(
        db,
        submission.id,
        max_points,
        points_for(ai_suggested_ratio(rules, percentages), max_points),
        points_for(final_ratio, max_points),
    )
    return points, assignment.course_id


def refresh_student_course_points(
    db: Session, course_id: int, student_id: int
) -> UserCoursePoints:
    evaluative_mode = retrieve_submission_mode_by_name(db, "Evaluative mode")
    latest_by_assignment = {}
    for row in retrieve_completed_points_for_student(
        db, course_id, student_id, evaluative_mode.id
    ):
        latest_by_assignment[row.assignment_id] = row
    latest = latest_by_assignment.values()
    return save_user_course_points(
        db,
        course_id,
        student_id,
        round(sum(row.final_points or 0 for row in latest if row.graded), 2),
        round(sum(row.max_points or 0 for row in latest), 2),
    )


def refresh_submission_points(db: Session, submission: Submission) -> SubmissionPoints:
    points, course_id = _save_points_for_submission(db, submission)
    if course_id:
        refresh_student_course_points(db, course_id, submission.user_id)
    return points


def refresh_course_points(db: Session, course_id: int) -> None:
    evaluative_mode = retrieve_submission_mode_by_name(db, "Evaluative mode")
    student_ids = set()
    for submission in retrieve_completed_submissions_in_course(
        db, course_id, evaluative_mode.id
    ):
        _save_points_for_submission(db, submission)
        student_ids.add(submission.user_id)
    for student_id in student_ids:
        refresh_student_course_points(db, course_id, student_id)
    db.commit()
