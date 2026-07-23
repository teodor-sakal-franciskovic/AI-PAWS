from ..dependencies.db import get_new_session
from ..repository.course import retrieve_rules_for_course
from ..utils.logger import logger


def generate_prompt_descriptions(course_id: int):
    logger.info("[BACKGROUND] Starting a background DB session...")
    db = get_new_session()
    try:
        logger.info(f"[BACKGROUND] Retrieving rules for course {course_id}...")
        rules = retrieve_rules_for_course(db, course_id)
        logger.info(f"[BACKGROUND] Retrieved {len(rules)} rules for course {course_id}")

        for rule in rules:
            logger.info(
                f"[BACKGROUND] Generating prompt_description for rule {rule.id}..."
            )
            # TODO: zameniti stvarnim LLM pozivom
            rule.prompt_description = f"Evaluate whether: {rule.user_description}"
            db.commit()
            logger.info(
                f"[BACKGROUND] Successfully generated prompt_description for rule {rule.id}"
            )

    except Exception as e:
        logger.error(f"[BACKGROUND] An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
