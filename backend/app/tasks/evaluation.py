from ..dependencies.db import get_new_session
from ..repository.submission import retrieve_by_id as retrieve_submission_by_id
from ..repository.submission import retrieve_rule_evaluations
from ..repository.user import retrieve_by_id as retrieve_user_by_id
from ..services.evaluation import latest_rule_evaluations
from ..services.historical_profile import (
    insert_historical_profile_snapshot,
    retrieve_updated_student_knowledge_from_evaluative_mode,
)
from ..utils.logger import logger


def update_student_knowledge_after_grading(submission_id: int, llm):
    logger.info(f"[BACKGROUND] Updating student knowledge after grading submission {submission_id}...")
    db = get_new_session()
    try:
        rules = latest_rule_evaluations(retrieve_rule_evaluations(db, submission_id))
        rule_evaluations = [
            (
                rule.rule_name,
                rule.rule_description,
                rule.final_fulfillment_value,
                rule.final_feedback_text,
            )
            for rule in rules
            if rule.final_fulfillment_value is not None
        ]
        updated_knowledge = retrieve_updated_student_knowledge_from_evaluative_mode(
            db, llm, rule_evaluations, submission_id
        )
        submission = retrieve_submission_by_id(db, submission_id)
        student = retrieve_user_by_id(db, submission.user_id)
        insert_historical_profile_snapshot(
            db, student, submission, updated_knowledge.updated_knowledge
        )
        logger.info(f"[BACKGROUND] Updated student knowledge after grading submission {submission_id}")
    except Exception as e:
        logger.error(f"[BACKGROUND] Failed to update student knowledge for submission {submission_id}: {e}")
        db.rollback()
    finally:
        db.close()
