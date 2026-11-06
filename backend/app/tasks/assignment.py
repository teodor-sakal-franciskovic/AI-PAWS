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
from ..services.points import refresh_submission_points
from ..services.rule_group import compile_rule_group
from ..llm.schema import LLMFeedbackResponse
from ..repository.assignment import retrieve_by_id as retrieve_assignment_by_id
from ..repository.rule import retrieve_rules_for_assignment
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


def retrieve_llm_grading(submission_id: int, llm):
    logger.info("[BACKGROUND] Starting a background DB session...")
    db = get_new_session()
    submission = db.get(Submission, submission_id)
    if submission is None:
        logger.error(f"[BACKGROUND] Submission {submission_id} not found")
        db.close()
        return
    try:
        assignment = retrieve_assignment_by_id(db, submission.assignment_id)
        rules = retrieve_rules_for_assignment(db, assignment.id)
        uncompiled_groups = {rule.rule_group_id for rule in rules if rule.needs_compiling}
        for rule_group_id in uncompiled_groups:
            try:
                compile_rule_group(db, rule_group_id, llm)
            except Exception as e:
                logger.warning(
                    f"[BACKGROUND] Couldn't compile rule group {rule_group_id}, grading from the instructor's text: {e}"
                )
                db.rollback()
        if uncompiled_groups:
            rules = retrieve_rules_for_assignment(db, assignment.id)

        prompt_rules = [rule for rule in rules if rule.include_in_prompt]
        logger.info(
            f"[BACKGROUND] Submission {submission_id}: {len(rules)} rules, {len(prompt_rules)} graded by the LLM"
        )

        llm_rule_evaluations = []
        if prompt_rules:
            logger.info("[BACKGROUND] Requesting LLM evaluation...")
            llm_rule_evaluations = request_evaluation(
                db, llm, submission, prompt_rules, assignment
            )

        logger.info("[BACKGROUND] Creating feedback objects...")
        create_feedback_objects_for_evaluative_mode(
            db, rules, llm_rule_evaluations, submission
        )

        logger.info("[BACKGROUND] Updating submission status to COMPLETED...")
        update_submission_status(db, submission, SubmissionStatus.COMPLETED)
        logger.info("[BACKGROUND] Successfully updated submission status to COMPLETED")
        refresh_submission_points(db, submission)
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
