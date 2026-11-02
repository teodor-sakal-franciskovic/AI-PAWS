from ..dependencies.db import get_new_session
from ..services.rule_group import compile_rule_group
from ..utils.logger import logger


def generate_prompt_descriptions(rule_group_id: int, llm):
    logger.info(f"[BACKGROUND] Compiling rules of rule group {rule_group_id}...")
    db = get_new_session()
    try:
        compile_rule_group(db, rule_group_id, llm)
        logger.info(f"[BACKGROUND] Compiled rules of rule group {rule_group_id}")
    except Exception as e:
        logger.error(f"[BACKGROUND] An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
