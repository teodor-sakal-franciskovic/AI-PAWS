import io
import zipfile

from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from ..models.assignment import Assignment
from ..models.assignment_group import AssignmentGroup
from ..models.user import User
from ..models.submission import Submission

from ..schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
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
    assignment_response: AssignmentResponse = create_assignment_response(db, assignment)
    return assignment_response


def retrieve_assignments(db: Session):
    logger.info("Retrieving all assignments...")
    assignments: list[Assignment] = retrieve_all(db)
    assignments_response: list[AssignmentResponse] = [
        create_assignment_response(db, assignment) for assignment in assignments
    ]
    return assignments_response


def retrieve_active_assignments_for_student(db: Session, user: User):
    logger.info(f"Retrieving active assignments for user {user.id}")
    submissions_with_assignments: list[Submission, Assignment] = (
        retrieve_active_assignments_for_group(db, user.group_id)
    )
    active_assignment_responses = []
    for submission, assignment in submissions_with_assignments:
        rule_feedbacks = retrieve_rule_feedbacks_for_submission(db, submission.id)
        logger.info(f"Rule feedbacks {rule_feedbacks} for submission {submission.id}")
        submission_response = SubmissionResponse(
            id=submission.id,
            text=submission.text,
            achieved_points_percentage=submission.achieved_points_percentage,
            submission_mode=retrieve_submission_mode_by_id(
                db, submission.submission_mode_id
            ).name,
            submitted_at=submission.submitted_at,
            status=submission.status,
            rule_feedbacks=rule_feedbacks,
        )
        finished_assignment_response = SubmittedSubmissionForAssignmentResponse(
            id=assignment.id,
            name=assignment.name,
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            submission=submission_response,
        )
        active_assignment_responses.append(finished_assignment_response)
    logger.info("Successfully retrieved active assignments")
    return active_assignment_responses


def retrieve_previous_assignments_for_student(
    db: Session,
    user: User,
) -> list[SubmittedSubmissionForAssignmentResponse]:
    logger.info(f"Retrieving finished assignments for the user {user.id}")
    submissions_with_assignments: list[Submission, Assignment] = (
        retrieve_past_submissions_with_assignments_for_user(db, user.id)
    )
    finished_assignment_responses = []
    for submission, assignment in submissions_with_assignments:
        rule_feedbacks = retrieve_rule_feedbacks_for_submission(db, submission.id)
        submission_response = SubmissionResponse(
            id=submission.id,
            text=submission.text,
            achieved_points_percentage=submission.achieved_points_percentage,
            submission_mode=retrieve_submission_mode_by_id(
                db, submission.submission_mode_id
            ).name,
            submitted_at=submission.submitted_at,
            status=submission.status,
            rule_feedbacks=rule_feedbacks,
        )
        finished_assignment_response = SubmittedSubmissionForAssignmentResponse(
            id=assignment.id,
            name=assignment.name,
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            submission=submission_response,
        )
        finished_assignment_responses.append(finished_assignment_response)
    logger.info("Successfully retrieved finished assignments")
    return finished_assignment_responses


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
            full_path = f"{ta_folder}/{student_filename}"

            zf.writestr(full_path, submission.file_bytes)

    zip_stream.seek(0)

    return StreamingResponse(
        zip_stream,
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f'attachment; filename="{assignment.name}.zip"'
        },
    )
