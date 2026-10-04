from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.submission import Submission, SubmissionStatus
from ..models.submission_mode import SubmissionMode
from ..repository.assignment import retrieve_by_id as retrieve_assignment_by_id
from ..repository.course import instructor_has_access
from ..repository.course import retrieve_by_id as retrieve_course_by_id
from ..repository.group import (
    retrieve_assigned_students_for_instructor,
    retrieve_student_ids_in_course_groups,
)
from ..repository.rule import retrieve_rules_for_assignment
from .chapter import extract_pdf_to_markdown
from ..repository.submission_mode import (
    retrieve_by_name as retrieve_submission_mode_by_name,
)
from ..repository.submission import (
    retrieve_by_id,
    retrieve_completed_evaluative_submissions,
    update_status,
)
from ..utils.logger import logger


def save_submission(
    db: Session,
    extracted_text: str,
    submission_mode_name: str,
    user_id: int,
    assignment_id: int,
    file_bytes,
    status: str,
    graded: bool = False,
    file_name: str | None = None,
):
    submission_mode: SubmissionMode = retrieve_submission_mode_by_name(
        db, submission_mode_name
    )
    logger.info(f"Submission mode for save submission: {submission_mode}")
    submission = Submission(
        text=extracted_text,
        user_id=user_id,
        submission_mode_id=submission_mode.id,
        graded=graded,
        assignment_id=assignment_id,
        file_bytes=file_bytes,
        file_name=file_name,
        status=status,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


PDF_CONTENT_TYPE = "application/pdf"


def create_evaluative_submission(
    db: Session,
    assignment_id: int,
    student_id: int,
    file_bytes: bytes,
    file_name: str | None,
    content_type: str | None,
) -> int:
    assignment = retrieve_assignment_by_id(db, assignment_id)
    evaluative_mode = retrieve_submission_mode_by_name(db, "Evaluative mode")
    if (
        not assignment
        or assignment.submission_mode_id != evaluative_mode.id
        or not retrieve_course_by_id(db, assignment.course_id)
    ):
        raise ApiError(404, "ASSIGNMENT_NOT_FOUND", "Evaluative assignment not found.")

    if not retrieve_student_ids_in_course_groups(db, assignment.course_id, [student_id]):
        raise ApiError(
            403,
            "ASSIGNMENT_ACCESS_DENIED",
            "You are not enrolled in this assignment's course.",
        )

    if not retrieve_rules_for_assignment(db, assignment_id):
        raise ApiError(
            409,
            "ASSIGNMENT_HAS_NO_RULES",
            "This assignment has no rules to grade against.",
        )

    if content_type != PDF_CONTENT_TYPE:
        raise ApiError(400, "VALIDATION_ERROR", "The file must be a PDF.")
    try:
        extracted_text = extract_pdf_to_markdown(file_bytes)
    except HTTPException:
        raise ApiError(400, "VALIDATION_ERROR", "The PDF couldn't be read.")

    submission = save_submission(
        db,
        extracted_text,
        "Evaluative mode",
        student_id,
        assignment_id,
        file_bytes,
        SubmissionStatus.PENDING,
        file_name=file_name,
    )
    return submission.id


def retrieve_submission(db: Session, submission_id: int) -> Submission:
    logger.info(f"Retrieving submission with id {submission_id}...")
    submission: Submission = retrieve_by_id(db, submission_id)
    logger.info("Successfully retrieved submission")
    return submission


def update_submission_status(
    db: Session, submission: Submission, status: SubmissionStatus
):
    logger.info(f"Updating submission {submission.id} status to {status}...")
    update_status(db, submission.id, status)
    logger.info("Successfully updated the submission status...")


def assignment_max_points(
    course_max_points: float | None, percentage_of_points_in_course: float | None
) -> float | None:
    if course_max_points is None or percentage_of_points_in_course is None:
        return None
    return round(course_max_points * percentage_of_points_in_course / 100, 2)


def _grading_submission(row, course_max_points: float | None) -> dict:
    max_points = assignment_max_points(
        course_max_points, row.percentage_of_points_in_course
    )
    result = None
    if row.graded:
        ratio = row.achieved_points_percentage or 0.0
        result = {
            "fulfillment_ratio": round(ratio, 4),
            "achieved_points": round(ratio * max_points, 2)
            if max_points is not None
            else None,
        }
    return {
        "submission_id": row.submission_id,
        "submission_status": row.status,
        "grading_status": "GRADED" if row.graded else "NOT_GRADED",
        "submitted_at": row.submitted_at,
        "assignment": {
            "id": row.assignment_id,
            "name": row.assignment_name,
            "start_date": row.assignment_start_date,
            "end_date": row.assignment_end_date,
            "max_points": max_points,
        },
        "result": result,
    }


def _grading_summary(submissions: list[dict]) -> dict:
    graded = [s for s in submissions if s["result"] is not None]
    return {
        "completed_submissions_count": len(submissions),
        "ungraded_submissions_count": len(submissions) - len(graded),
        "achieved_points": round(
            sum(s["result"]["achieved_points"] or 0 for s in graded), 2
        ),
        "max_points": round(
            sum(s["assignment"]["max_points"] or 0 for s in submissions), 2
        ),
    }


def get_evaluative_submissions_for_my_students(
    db: Session, course_id: int, instructor_id: int
) -> dict:
    course = retrieve_course_by_id(db, course_id)
    if not course:
        raise ApiError(404, "COURSE_NOT_FOUND", "Course not found.")
    if not instructor_has_access(db, course, instructor_id):
        raise ApiError(
            403, "COURSE_ACCESS_DENIED", "You do not have access to this course."
        )

    students = retrieve_assigned_students_for_instructor(db, course_id, instructor_id)
    evaluative_mode = retrieve_submission_mode_by_name(db, "Evaluative mode")
    rows = retrieve_completed_evaluative_submissions(
        db, course_id, [s.id for s in students], evaluative_mode.id
    )

    latest_by_student_assignment = {}
    for row in rows:
        latest_by_student_assignment[(row.user_id, row.assignment_id)] = row

    submissions_by_student: dict[int, list[dict]] = {}
    for row in latest_by_student_assignment.values():
        submissions_by_student.setdefault(row.user_id, []).append(
            _grading_submission(row, course.max_amount_of_points)
        )

    students_with_submissions = []
    for student in students:
        submissions = submissions_by_student.get(student.id, [])
        students_with_submissions.append(
            {
                "student_id": student.id,
                "student_index": student.index,
                "name": student.name,
                "surname": student.surname,
                "summary": _grading_summary(submissions),
                "submissions": submissions,
            }
        )
    return {"students_with_submissions": students_with_submissions}
