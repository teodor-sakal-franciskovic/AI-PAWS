from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..llm.prompt import (
    call_initial_interactive_prompt,
    generate_initial_interactive_prompt,
    generate_initial_interactive_user_prompt,
    generate_system_prompt,
    initialise_format_instructions,
)
from ..models.historical_profile import HistoricalProfile
from ..models.prompt_template import PromptTemplate
from ..models.submission import Submission
from ..models.user import User
from ..models.feedback import Feedback
from ..llm.schema import LLMRuleFeedback, LLMFeedbackResponse
from ..repository.historical_profile import retrieve_latest
from ..repository.prompt_template import retrieve_by_purpose
from ..repository.rule import retrieve_rules_for_chapter
from ..utils.feedback import (
    generate_initial_interactive_mode_feedbacks,
    create_interactive_mode_feedbacks_response,
)
from ..utils.logger import logger
from ..schemas.feedback import InteractiveFeedbackResponse


def request_initial_interactive_feedback(
    db: Session, llm, submission: Submission, user: User, chapter_name: str
) -> LLMFeedbackResponse:
    logger.info(f"Retrieving initial interactive prompt template for user {user.id}...")
    initial_interactive_prompt_template: PromptTemplate = retrieve_by_purpose(
        db, "Initial Interactive"
    )
    logger.info("Successfully retrieved initial interactive prompt template")

    logger.info(
        f"Retrieving knowledge summarisation prompt template for user {user.id}..."
    )
    knowledge_summarisation_prompt_template: PromptTemplate = retrieve_by_purpose(
        db, "Knowledge Summarisation"
    )
    logger.info("Successfully retrieved knowledge summarisation prompt template")

    logger.info(f"Retrieving the latest historical profile for {user.id}...")
    latest_historical_profile: HistoricalProfile = retrieve_latest(db, user.id)
    logger.info("Successfully retrieved the latest historical profile")

    logger.info(f"Retrieving prompt rules for chapter {chapter_name} user {user.id}")
    rules = retrieve_rules_for_chapter(db, chapter_name, include_in_prompt=True)
    logger.info(f"Successfully retrieved prompt rules for chapter {chapter_name}")

    logger.info(f"Forming system prompt: user {user.id}")
    system_prompt = generate_system_prompt(
        latest_historical_profile, initial_interactive_prompt_template
    )
    logger.info("Successfully formed system prompt")

    logger.info(f"Forming user prompt: user {user.id}")
    user_prompt = generate_initial_interactive_user_prompt(
        initial_interactive_prompt_template,
        knowledge_summarisation_prompt_template,
        rules,
        submission,
    )
    logger.info("Successfully formed user prompt")

    logger.info(f"Forming the whole prompt: user {user.id}")
    parser, format_instructions = initialise_format_instructions("LLMFeedbackResponse")
    prompt = generate_initial_interactive_prompt(format_instructions)
    logger.info("Successfully formed the whole prompt")

    logger.info(f"Calling GPT API... user {user.id}")
    try:
        response = call_initial_interactive_prompt(
            prompt, llm, parser, system_prompt, user_prompt
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while calling the GPT API: {e}",
        )
    logger.info("Successfully received the response from the GPT API")
    logger.info(f"Response {response}")
    return response


def create_feedback_objects_for_interactive_mode(
    db: Session,
    llm_rule_feedbacks: list[LLMRuleFeedback],
    chapter_name: str,
    submission: Submission,
):
    logger.info(f"Retrieving prompt rules for chapter {chapter_name}")
    rules = retrieve_rules_for_chapter(db, chapter_name, include_in_prompt=True)
    logger.info(f"Successfully retrieved prompt rules for chapter {chapter_name}")

    feedbacks: list[Feedback] = generate_initial_interactive_mode_feedbacks(
        db, rules, llm_rule_feedbacks, submission
    )
    feedbacks_response: list[InteractiveFeedbackResponse] = (
        create_interactive_mode_feedbacks_response(db, feedbacks)
    )
    return feedbacks_response
