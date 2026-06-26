from sqlalchemy.orm import Session

from ..models.submission import Submission, SubmissionStatus
from ..models.submission_mode import SubmissionMode
from ..repository.chapter import retrieve_by_name as retrieve_chapter_by_name
from ..repository.submission_mode import (
    retrieve_by_name as retrieve_submission_mode_by_name,
)
from ..repository.submission import retrieve_by_id, update_status
from ..utils.logger import logger


def save_submission(
    db: Session,
    extracted_text: str,
    chapter_name: str,
    submission_mode_name: str,
    user_id: int,
    assignment_id: int,
    file_bytes,
    status: str,
    graded: bool = False,
):
    chapter = retrieve_chapter_by_name(db, chapter_name)
    logger.info(f"Chapter for save submission: {chapter}")
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
        status=status,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


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
