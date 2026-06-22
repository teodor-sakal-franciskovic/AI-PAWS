from ..dependencies.db import get_new_session
from ..models.submission import Submission, SubmissionStatus
from ..models.user import User
from ..services.submission import update_submission_status
from ..services.historical_profile import insert_historical_profile_snapshot
from ..services.feedback import (
    request_initial_interactive_feedback,
    create_feedback_objects_for_interactive_mode,
    request_evaluation,
    create_feedback_objects_for_evaluative_mode,
)
from ..llm.schema import LLMFeedbackResponse, LLMEvaluationResponse
from ..utils.logger import logger


def retrieve_llm_feedback(submission_id: int, user_id: int, chapter_name: str, llm):
    logger.info("[BACKGROUND] Starting a background DB session...")
    db = get_new_session()
    try:
        logger.info(f"[BACKGROUND] Retrieving submission {submission_id}")
        submission = db.get(Submission, submission_id)
        logger.info(f"[BACKGROUND] Successfully retrieved submission {submission_id}")

        logger.info(f"[BACKGROUND] Retrieving user {user_id}...")
        user = db.get(User, user_id)
        logger.info(f"[BACKGROUND] Successfully retrieved user {user_id}")

        logger.info("[BACKGROUND] Requesting LLM feedback...")
        llm_feedback_response: LLMFeedbackResponse = (
            request_initial_interactive_feedback(
                db, llm, submission, user, chapter_name
            )
        )

        logger.info("[BACKGROUND] Creating interactive feedback object...")
        create_feedback_objects_for_interactive_mode(
            db, llm_feedback_response.feedback, chapter_name, submission
        )

        logger.info("[BACKGROUND] Inserting historical profile...")
        insert_historical_profile_snapshot(
            db, user, submission, llm_feedback_response.updated_knowledge
        )

        logger.info("[BACKGROUND] Updating submission status to COMPLETED...")
        update_submission_status(db, submission, SubmissionStatus.COMPLETED)
        logger.info("[BACKGROUND] Successfully updated submission status to COMPLETED")
        db.commit()
    except Exception as e:
        logger.info(f"[BACKGROUND] An error occurred: {e}")
        db.rollback()
        logger.info("[BACKGROUND] Updating submission status to FAILED...")
        update_submission_status(db, submission, SubmissionStatus.FAILED)
        logger.info("[BACKGROUND] Successfully updated submission status to FAILED")
        db.commit()
    finally:
        db.close()


def retrieve_llm_grading(submission_id: int, user_id: int, chapter_name: str, llm):
    logger.info("[BACKGROUND] Starting a background DB session...")
    db = get_new_session()
    try:
        logger.info(f"[BACKGROUND] Retrieving submission {submission_id}")
        submission = db.get(Submission, submission_id)
        logger.info(f"[BACKGROUND] Successfully retrieved submission {submission_id}")

        logger.info(f"[BACKGROUND] Retrieving user {user_id}...")
        user = db.get(User, user_id)
        logger.info(f"[BACKGROUND] Successfully retrieved user {user_id}")

        logger.info("[BACKGROUND] Requesting LLM evaluation...")
        llm_evaluation_response: LLMEvaluationResponse = request_evaluation(
            db, llm, submission, user, chapter_name
        )

        logger.info("[BACKGROUND] Creating feedback objects...")
        create_feedback_objects_for_evaluative_mode(
            db, llm_evaluation_response.evaluation, chapter_name, submission
        )

        logger.info("[BACKGROUND] Updating submission status to COMPLETED...")
        update_submission_status(db, submission, SubmissionStatus.COMPLETED)
        logger.info("[BACKGROUND] Successfully updated submission status to COMPLETED")
        db.commit()
    except Exception as e:
        logger.info(f"[BACKGROUND] An error occurred: {e}")
        db.rollback()
        logger.info("[BACKGROUND] Updating submission status to FAILED...")
        update_submission_status(db, submission, SubmissionStatus.FAILED)
        logger.info("[BACKGROUND] Successfully updated submission status to FAILED")
        db.commit()
    finally:
        db.close()
