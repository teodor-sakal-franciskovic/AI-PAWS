from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..llm.prompt import (
    call_prompt,
    generate_whole_prompt,
    generate_user_prompt_for_initial_interactive_and_evaluative_mode,
    generate_additional_interactive_user_prompt,
    generate_system_prompt,
    initialise_format_instructions,
)
from ..models.historical_profile import HistoricalProfile
from ..models.prompt_template import PromptTemplate
from ..models.submission import Submission
from ..models.user import User
from ..models.rule import Rule
from ..models.feedback import Feedback
from ..llm.schema import (
    LLMRuleFeedback,
    LLMFeedbackResponse,
    LLMAdditionalFeedbackResponse,
    LLMRuleEvaluation,
)
from ..repository.historical_profile import retrieve_latest
from ..repository.prompt_template import retrieve_by_purpose
from ..repository.rule import (
    retrieve_rules_for_chapter,
    retrieve_by_id as retrieve_rule_by_id,
)
from ..repository.feedback import (
    retrieve_by_id as retrieve_feedback_by_id,
    update_with_additional_text,
    update_is_valid,
)
from ..utils.feedback import (
    generate_initial_interactive_mode_feedbacks,
    create_interactive_mode_feedbacks_response,
    generate_evaluative_mode_feedbacks_and_fulfillments,
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
        db, "Knowledge Summarisation Initial Interactive"
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
    user_prompt = generate_user_prompt_for_initial_interactive_and_evaluative_mode(
        initial_interactive_prompt_template,
        knowledge_summarisation_prompt_template,
        rules,
        submission,
    )
    logger.info("Successfully formed user prompt")

    logger.info(f"Forming the whole prompt: user {user.id}")
    parser, format_instructions = initialise_format_instructions("LLMFeedbackResponse")
    prompt = generate_whole_prompt(format_instructions)
    logger.info("Successfully formed the whole prompt")

    logger.info(f"Calling GPT API... user {user.id}")
    try:
        response = call_prompt(prompt, llm, parser, system_prompt, user_prompt)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while calling the GPT API: {e}",
        )
    logger.info("Successfully received the response from the GPT API")
    logger.info(f"Response {response}")
    return response


def request_additional_interactive_feedback(
    db: Session,
    llm,
    latest_historical_profile: HistoricalProfile,
    submission: Submission,
    feedback: Feedback,
) -> LLMAdditionalFeedbackResponse:
    logger.info("Retrieving additonal interactive prompt template...")
    additional_interactive_prompt_template: PromptTemplate = retrieve_by_purpose(
        db, "Additional Interactive"
    )
    logger.info("Successfully retrieved additional interactive prompt template")

    logger.info("Retrieving knowledge summarisation prompt template...")
    knowledge_summarisation_prompt_template: PromptTemplate = retrieve_by_purpose(
        db, "Knowledge Summarisation Additional Interactive"
    )
    logger.info("Successfully retrieved knowledge summarisation prompt template")

    logger.info(f"Retrieving rule for feedback with id {feedback.id}...")
    rule: Rule = retrieve_rule_by_id(db, feedback.rule_id)

    logger.info("Forming system prompt...")
    system_prompt = generate_system_prompt(
        latest_historical_profile, additional_interactive_prompt_template
    )
    logger.info("Successfully formed system prompt")

    logger.info("Forming user prompt...")
    user_prompt = generate_additional_interactive_user_prompt(
        additional_interactive_prompt_template,
        knowledge_summarisation_prompt_template,
        submission.text,
        rule.description,
        feedback.feedback_text,
    )
    logger.info("Successfully formed user prompt")

    logger.info("Forming the whole prompt...")
    parser, format_instructions = initialise_format_instructions(
        "LLMAdditionalFeedbackResponse"
    )
    prompt = generate_whole_prompt(format_instructions)
    logger.info("Successfully formed the whole prompt")

    logger.info("Calling GPT API...")
    try:
        response = call_prompt(prompt, llm, parser, system_prompt, user_prompt)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while calling the GPT API: {e}",
        )
    logger.info("Successfully received the response from the GPT API")
    return response


def request_evaluation(
    db: Session, llm, submission: Submission, user: User, chapter_name: str
):
    logger.info(f"Retrieving evaluation prompt template for user {user.id}...")
    evaluative_prompt_template: PromptTemplate = retrieve_by_purpose(db, "Evaluative")
    logger.info("Successfully retrieved evaluation prompt template")

    logger.info(
        f"Retrieving knowledge summarisation prompt template for user {user.id}..."
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
        latest_historical_profile, evaluative_prompt_template
    )
    logger.info("Successfully formed system prompt")

    logger.info(f"Forming user prompt: user {user.id}")
    user_prompt = generate_user_prompt_for_initial_interactive_and_evaluative_mode(
        evaluative_prompt_template,
        None,
        rules,
        submission,
    )
    logger.info("Successfully formed user prompt")

    logger.info(f"Forming the whole prompt: user {user.id}")
    parser, format_instructions = initialise_format_instructions(
        "LLMEvaluationResponse"
    )
    prompt = generate_whole_prompt(format_instructions)
    logger.info("Successfully formed the whole prompt")

    logger.info(f"Calling GPT API... user {user.id}")
    try:
        response = call_prompt(prompt, llm, parser, system_prompt, user_prompt)
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


def create_feedback_objects_for_evaluative_mode(
    db: Session,
    llm_rule_evaluations: list[LLMRuleEvaluation],
    chapter_name: str,
    submission: Submission,
):
    logger.info(f"Retrieving prompt rules for chapter {chapter_name}")
    rules = retrieve_rules_for_chapter(db, chapter_name, include_in_prompt=False)
    logger.info(f"Successfully retrieved prompt rules for chapter {chapter_name}")

    evaluations = generate_evaluative_mode_feedbacks_and_fulfillments(
        db, rules, llm_rule_evaluations, submission
    )
    return evaluations


def retrieve_feedback(db: Session, feedback_id: int) -> Feedback:
    logger.info(f"Retrieving feedback with id {feedback_id}...")
    feedback: Feedback = retrieve_feedback_by_id(db, feedback_id)
    logger.info("Successfully retrieved feedback")
    return feedback


def update_feedback_with_additional_context(
    db: Session, feedback_id: int, additional_feedback: str
):
    logger.info(f"Updating feedback {feedback_id} with additional context...")
    feedback: Feedback = update_with_additional_text(
        db, feedback_id, additional_feedback
    )
    logger.info(
        f"Successfully updated feedback with additional context: {additional_feedback}"
    )
    rule: Rule = retrieve_rule_by_id(db, feedback.rule_id)
    feedback_response = InteractiveFeedbackResponse(
        id=feedback.id,
        feedback_text=feedback.feedback_text,
        initially_fulfilled=feedback.initially_fulfilled,
        rule_name=rule.name,
        rule_description=rule.description,
        additional_feedback_text=feedback.additional_text,
        is_valid=feedback.is_valid,
    )
    return feedback_response


def invalidate_feedback(db: Session, feedback_id: int):
    update_is_valid(db, feedback_id, False)
