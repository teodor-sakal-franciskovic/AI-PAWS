from ..dependencies.db import get_new_session
from ..repository.rule_group import retrieve_rules_needing_prompt
from ..utils.logger import logger


def generate_prompt_descriptions(rule_group_id: int):
    logger.info("[BACKGROUND] Starting a background DB session...")
    db = get_new_session()
    try:
        logger.info(f"[BACKGROUND] Retrieving rules for rule group {rule_group_id}...")
        rules = retrieve_rules_needing_prompt(db, rule_group_id)
        logger.info(
            f"[BACKGROUND] Retrieved {len(rules)} rules for rule group {rule_group_id}"
        )

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
