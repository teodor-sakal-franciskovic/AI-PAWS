from typing import List, Dict, Any

import pandas as pd
from fastapi import HTTPException

from ..dependencies.db import get_new_session
from ..models.rule import Rule
from ..models.prompt_template import PromptTemplate
from ..models.user import User
from ..services.historical_profile import insert_initial_student_historical_profile
from ..repository.rule import retrieve_all as retrieve_all_rules
from ..repository.user import retrieve_by_index as retrieve_user_by_index
from ..repository.prompt_template import (
    retrieve_by_purpose as retrieve_prompt_template_by_purpose,
)
from ..utils.user import build_students_data
from ..utils.logger import logger
from ..llm.prompt import (
    generate_user_prompt_for_initial_student_knowledge_creation,
    initialise_format_instructions,
    generate_whole_prompt,
    call_llm,
)


def generate_initial_student_knowledge(df: pd.DataFrame, llm):
    db = get_new_session()
    try:
        logger.info("[BACKGROUND] Retrieving all rules...")
        rules: List[Rule] = retrieve_all_rules(db)
        rule_descriptions = {r.name: r.description for r in rules}
        logger.info("[BACKGROUND] Successfully retrieved all rules")

        logger.info("[BACKGROUND] Building students data from the df...")
        students_data: List[Dict[str, Any]] = build_students_data(df, rule_descriptions)
        logger.info(
            f"[BACKGROUND] Successfully built students data from the df: {students_data}"
        )

        logger.info("[BACKGROUND] Retrieving prompts...")
        initial_interactive_prompt_template: PromptTemplate = (
            retrieve_prompt_template_by_purpose(
                db, "Initial Student Knowledge Creation"
            )
        )
        system_prompt = initial_interactive_prompt_template.system_text
        logger.info("[BACKGROUND] Successfully retrieved prompts")

        for data in students_data:
            index = data.get("student_index")
            logger.info(
                f"[BACKGROUND] Generating initial student knowledge for student {index}"
            )
            user_prompt = generate_user_prompt_for_initial_student_knowledge_creation(
                initial_interactive_prompt_template, data
            )
            parser, format_instructions = initialise_format_instructions(
                "LLMInitialKnowledgeResponse"
            )
            prompt = generate_whole_prompt(format_instructions)
            logger.info("[BACKGROUND] Calling GPT API...")
            try:
                response = call_llm(prompt, llm, parser, system_prompt, user_prompt)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Something went wrong while calling the GPT API: {e}",
                )
            logger.info(
                f"[BACKGROUND] Initial student knowledge: {response.initial_student_knowledge}"
            )
            user: User = retrieve_user_by_index(db, index)
            insert_initial_student_historical_profile(
                db, user.id, response.initial_student_knowledge
            )
    except Exception as e:
        logger.info(f"[BACKGROUND] An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
