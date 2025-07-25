from sqlalchemy.orm import Session

from ..models.assignment import Assignment
from ..models.assignment_group import AssignmentGroup
from ..models.user import User
from ..models.submission import Submission

from ..schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    FinishedAssignmentResponse,
)
from ..schemas.submission import SubmissionResponse

from ..utils.assignment import create_assignment_response
from ..utils.logger import logger

from ..repository.assignment import (
    retrieve_active_assignments_for_group,
    retrieve_past_submissions_with_assignments_for_user,
)
from ..repository.submission import retrieve_rule_feedbacks_for_submission
from ..repository.submission_mode import retrieve_by_id


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


def retrieve_active_assignments_for_student(db: Session, user: User):
    logger.info(f"Retrieving active assignments for user {user.id}")
    assignments: list[Assignment] = retrieve_active_assignments_for_group(
        db, user.group_id
    )
    logger.info("Successfully retrieved active assignments")
    assignment_responses: list[AssignmentResponse] = [
        create_assignment_response(db, assignment) for assignment in assignments
    ]
    return assignment_responses


def retrieve_previous_assignments_for_student(
    db: Session,
    user: User,
) -> list[FinishedAssignmentResponse]:
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
            gd_file_id=submission.gd_file_id,
            gd_file_link=submission.gd_file_link,
            achieved_points_percentage=submission.achieved_points_percentage,
            submission_mode=retrieve_by_id(db, submission.submission_mode_id).name,
            submitted_at=submission.submitted_at,
            rule_feedbacks=rule_feedbacks,
        )
        finished_assignment_response = FinishedAssignmentResponse(
            id=assignment.id,
            name=assignment.name,
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            submission=submission_response,
        )
        finished_assignment_responses.append(finished_assignment_response)
    logger.info("Successfully retrieved finished assignments")
    return finished_assignment_responses
