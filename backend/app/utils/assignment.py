from sqlalchemy.orm import Session

from ..models.assignment import Assignment
from ..models.submission_mode import SubmissionMode


from ..schemas.assignment import AssignmentResponse

from ..repository.submission_mode import (
    retrieve_by_id as retrieve_submission_mode_by_id,
)
from ..repository.chapter import retrieve_by_id as retrieve_chapter_by_id


def create_assignment_response(db: Session, assignment: Assignment):
    submission_mode: SubmissionMode = retrieve_submission_mode_by_id(
        db, assignment.submission_mode_id
    )
    chapter = retrieve_chapter_by_id(db, assignment.chapter_id)
    assignment_response = AssignmentResponse(
        id=assignment.id,
        name=assignment.name,
        start_date=assignment.start_date,
        end_date=assignment.end_date,
        submission_mode_id=submission_mode.id,
        submission_mode_name=submission_mode.name,
        chapter_id=chapter.id,
        chapter_name=chapter.name,
    )
    return assignment_response
