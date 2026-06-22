import io
import zipfile

from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from urllib.parse import quote

from ..models.assignment import Assignment
from ..models.assignment_group import AssignmentGroup
from ..models.user import User
from ..models.submission import Submission

from ..schemas.assignment import (
    AssignmentCreate,
    SubmittedSubmissionForAssignmentResponse,
)
from ..schemas.submission import SubmissionResponse

from ..utils.assignment import create_assignment_response
from ..utils.logger import logger

from ..repository.assignment import (
    retrieve_active_assignments_for_group,
    retrieve_past_submissions_with_assignments_for_user,
    retrieve_by_id as retrieve_assignment_by_id,
    retrieve_all,
)
from ..repository.submission import (
    retrieve_rule_feedbacks_for_submission,
    retrieve_by_assignment_id,
)
from ..repository.submission_mode import (
    retrieve_by_id as retrieve_submission_mode_by_id,
)
from ..repository.chapter import retrieve_by_id as retrieve_chapter_by_id


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
        assignment_group = AssignmentGroup(
            assignment_id=assignment.id, group_id=group_id
        )
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
    submissions_with_assignments = retrieve_active_assignments_for_group(
        db, user.group_id, user.id
    )
    responses = _build_assignment_responses(db, submissions_with_assignments)
    logger.info("Successfully retrieved active assignments")
    return responses


def retrieve_previous_assignments_for_student(db: Session, user: User):
    logger.info(f"Retrieving finished assignments for the user {user.id}")
    submissions_with_assignments = retrieve_past_submissions_with_assignments_for_user(
        db, user.group_id, user.id
    )
    responses = _build_assignment_responses(db, submissions_with_assignments)
    logger.info("Successfully retrieved finished assignments")
    return responses


def retrieve_submission_files_for_assignment(db: Session, assignment_id: int):
    logger.info(f"Retrieving assignment for id {assignment_id}...")
    assignment: Assignment = retrieve_assignment_by_id(db, assignment_id)
    logger.info(f"Successfully retrieved assignment: {assignment.name}")

    logger.info("Retrieving submissions with students and TAs...")
    submissions_with_student_and_ta_info = retrieve_by_assignment_id(db, assignment_id)
    logger.info(
        f"Successfully retrieved submissions with students and TAs: {submissions_with_student_and_ta_info}"
    )

    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for submission, student, ta in submissions_with_student_and_ta_info:
            logger.info(f"Submission: {submission.id}")
            logger.info(f"Student: {student.index}")
            logger.info(f"TA: {ta.name}")
            if not submission.file_bytes:
                continue
            ta_folder = f"{ta.name}_{ta.surname}" if ta else "Unassigned"
            student_filename = f"{student.index}_{student.name}_{student.surname}.pdf"
            zf.writestr(f"{ta_folder}/{student_filename}", submission.file_bytes)

    zip_stream.seek(0)
    encoded_filename = quote(f"{assignment.name}.zip")
    return StreamingResponse(
        zip_stream,
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )
