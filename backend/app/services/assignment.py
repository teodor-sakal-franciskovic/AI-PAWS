import re
import tempfile
import zipfile
from typing import IO

from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.assignment import Assignment
from ..models.course_group import CourseGroup
from ..models.submission import Submission
from ..models.user import User
from ..repository.assignment import (
    retrieve_active_assignments_for_group,
    retrieve_all,
    retrieve_course_assignments,
    retrieve_latest_submission_files,
    retrieve_past_submissions_with_assignments_for_user,
    retrieve_rule_group_summaries,
    retrieve_submitted_counts,
)
from ..repository.assignment import (
    retrieve_by_id as retrieve_assignment_by_id,
)
from ..repository.chapter import retrieve_by_id as retrieve_chapter_by_id
from ..repository.group import retrieve_group_ids_for_student
from ..repository.submission import retrieve_rule_feedbacks_for_submission
from ..repository.submission_mode import (
    retrieve_by_id as retrieve_submission_mode_by_id,
)
from ..schemas.assignment import (
    AssignmentCreate,
    SubmittedSubmissionForAssignmentResponse,
)
from ..schemas.submission import SubmissionResponse
from ..utils.assignment import create_assignment_response
from ..utils.logger import logger
from .course import require_course_access


def _build_submission_response(db: Session, submission: Submission):
    if not submission:
        return {}
    rule_feedbacks = retrieve_rule_feedbacks_for_submission(db, submission.id)
    return SubmissionResponse(
        id=submission.id,
        text=submission.text,
        achieved_points_percentage=submission.achieved_points_percentage,
        submission_mode=retrieve_submission_mode_by_id(
            db, submission.submission_mode_id
        ).name,
        submitted_at=submission.submitted_at,
        status=submission.status,
        rule_feedbacks=rule_feedbacks,
        file_bytes=submission.file_bytes,
    )


def _build_assignment_responses(db: Session, submissions_with_assignments):
    responses = []
    for assignment, submission in submissions_with_assignments:
        responses.append(
            SubmittedSubmissionForAssignmentResponse(
                id=assignment.id,
                name=assignment.name,
                start_date=assignment.start_date,
                end_date=assignment.end_date,
                submission=_build_submission_response(db, submission),
                submission_mode=retrieve_submission_mode_by_id(
                    db, assignment.submission_mode_id
                ).name,
                chapter_id=assignment.chapter_id,
                chapter_name=retrieve_chapter_by_id(db, assignment.chapter_id).name,
            )
        )
    return responses


def create_assignment(db: Session, body: AssignmentCreate):
    assignment = Assignment(
        name=body.name,
        start_date=body.start_date,
        end_date=body.end_date,
        submission_mode_id=body.submission_mode_id,
        chapter_id=body.chapter_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    for group_id in body.group_ids:
        assignment_group = CourseGroup(assignment_id=assignment.id, group_id=group_id)
        db.add(assignment_group)
    db.commit()
    return create_assignment_response(db, assignment)


def retrieve_assignments(db: Session):
    logger.info("Retrieving all assignments...")
    assignments: list[Assignment] = retrieve_all(db)
    logger.info("Successfully retrieved all assignments")
    return [create_assignment_response(db, assignment) for assignment in assignments]


def retrieve_active_assignments_for_student(db: Session, user: User):
    logger.info(f"Retrieving active assignments for user {user.id}")
    group_ids = retrieve_group_ids_for_student(db, user.id)
    submissions_with_assignments = retrieve_active_assignments_for_group(
        db, group_ids, user.id
    )
    responses = _build_assignment_responses(db, submissions_with_assignments)
    logger.info("Successfully retrieved active assignments")
    return responses


def retrieve_previous_assignments_for_student(db: Session, user: User):
    logger.info(f"Retrieving finished assignments for the user {user.id}")
    group_ids = retrieve_group_ids_for_student(db, user.id)
    submissions_with_assignments = retrieve_past_submissions_with_assignments_for_user(
        db, group_ids, user.id
    )
    responses = _build_assignment_responses(db, submissions_with_assignments)
    logger.info("Successfully retrieved finished assignments")
    return responses


def get_submission_overview(db: Session, course_id: int, instructor_id: int) -> dict:
    course = require_course_access(db, course_id, instructor_id)
    assignments = retrieve_course_assignments(db, course_id)
    assignment_ids = [assignment.id for assignment in assignments]
    submitted_counts = retrieve_submitted_counts(db, assignment_ids)

    rule_groups_by_assignment: dict[int, list[dict]] = {}
    for row in retrieve_rule_group_summaries(db, assignment_ids):
        rule_groups_by_assignment.setdefault(row.assignment_id, []).append(
            {
                "id": row.id,
                "name": row.name,
                "percentage_of_points_in_assignment": row.percentage_of_points_in_assignment,
                "rules_count": row.rules_count,
            }
        )

    return {
        "course": {"id": course.id, "name": course.name},
        "assignments": [
            {
                "id": assignment.id,
                "name": assignment.name,
                "start_date": assignment.start_date,
                "end_date": assignment.end_date,
                "submission_mode_id": assignment.submission_mode_id,
                "percentage_of_points_in_course": assignment.percentage_of_points_in_course,
                "submitted_count": submitted_counts.get(assignment.id, 0),
                "rule_groups": rule_groups_by_assignment.get(assignment.id, []),
            }
            for assignment in assignments
        ],
    }


ZIP_IN_MEMORY_LIMIT = 50 * 1024 * 1024


def _zip_safe_name(value: str) -> str:
    return re.sub(r'[\\/:*?"<>|\x00-\x1f]', "-", value).strip() or "unnamed"


def build_submissions_zip(
    db: Session, course_id: int, assignment_id: int, instructor_id: int
) -> tuple[IO[bytes], str]:
    require_course_access(db, course_id, instructor_id)
    assignment = retrieve_assignment_by_id(db, assignment_id)
    if not assignment or assignment.course_id != course_id:
        raise ApiError(404, "ASSIGNMENT_NOT_FOUND", "Assignment not found in this course.")

    archive = tempfile.SpooledTemporaryFile(max_size=ZIP_IN_MEMORY_LIMIT)
    with zipfile.ZipFile(archive, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for row in retrieve_latest_submission_files(db, assignment_id, course_id):
            folder = (
                _zip_safe_name(f"{row.instructor_name}_{row.instructor_surname}")
                if row.instructor_id
                else "Unassigned"
            )
            student = row.student_index or f"student-{row.student_id}"
            file_name = _zip_safe_name(f"{student}_{row.student_name}_{row.student_surname}")
            zf.writestr(f"{folder}/{file_name}.pdf", row.file_bytes)
    archive.seek(0)
    return archive, f"assignment-{assignment_id}-submissions.zip"
