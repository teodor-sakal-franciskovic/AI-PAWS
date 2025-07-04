from sqlalchemy.orm import Session

from ..models.chapter import Chapter
from ..models.submission import Submission
from ..models.submission_mode import SubmissionMode
from ..repository.chapter import retrieve_by_name as retrieve_chapter_by_name
from ..repository.submission_mode import (
    retrieve_by_name as retrieve_submission_mode_by_name,
)
from ..repository.submission import retrieve_by_id
from ..utils.logger import logger


def save_submission(
    db: Session,
    file_id: str,
    file_link: str,
    extracted_text: str,
    chapter_name: str,
    submission_mode_name: str,
    user_id: int,
):
    chapter: Chapter = retrieve_chapter_by_name(db, chapter_name)
    logger.info(f"Chapter for save submission: {chapter}")
    submission_mode: SubmissionMode = retrieve_submission_mode_by_name(
        db, submission_mode_name
    )
    logger.info(f"Submission mode for save submission: {submission_mode}")
    submission = Submission(
        text=extracted_text,
        gd_file_id=file_id,
        gd_file_link=file_link,
        user_id=user_id,
        chapter_id=chapter.id,
        submission_mode_id=submission_mode.id,
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
