import re
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..llm.prompt import (
    call_llm,
    call_llm_with_checks,
    generate_user_prompt_for_initial_interactive_and_evaluative_mode,
    generate_additional_interactive_user_prompt,
    generate_evaluative_user_prompt,
    generate_system_prompt,
)
from ..models.assignment import Assignment
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
    LLMEvaluationResponse,
    LLMRuleEvaluation,
)
from ..repository.course import retrieve_feedback_language_name
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

DEFAULT_FEEDBACK_LANGUAGE = "the language of the paper"
MAX_PARALLEL_GROUP_CALLS = 5


def _call_llm_with_retry(
    llm, response_schema, system_prompt, user_prompt, expected_count: int, count_fn
):
    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            response = call_llm(llm, response_schema, system_prompt, user_prompt)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Something went wrong while calling the LLM: {e}",
            )
        actual_count = count_fn(response)
        logger.info(
            f"Attempt {attempt + 1}: received {actual_count}/{expected_count} items"
        )
        if actual_count == expected_count:
            logger.info("LLM response matches expected count")
            break
        if attempt < max_retries - 1:
            logger.warning(
                f"Mismatch in count. Retrying... ({attempt + 1}/{max_retries})"
            )
    if response is not None and count_fn(response) != expected_count:
        logger.warning(
            f"LLM response still invalid after {max_retries} attempts. "
            f"Expected {expected_count}, got {count_fn(response)}. Continuing anyway."
        )
    return response


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
    number_of_rules = len(rules)
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
        chapter_name,
    )
    logger.info("Successfully formed user prompt")

    logger.info(f"Calling the LLM... user {user.id}")
    response = _call_llm_with_retry(
        llm,
        LLMFeedbackResponse,
        system_prompt,
        user_prompt,
        number_of_rules,
        lambda r: len(r.feedback),
    )
    logger.info("Successfully received the response from the LLM")
    return response


def request_additional_interactive_feedback(
    db: Session,
    llm,
    latest_historical_profile: HistoricalProfile,
    submission: Submission,
    feedback: Feedback,
) -> LLMAdditionalFeedbackResponse:
    logger.info("Retrieving additional interactive prompt template...")
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

    logger.info("Calling the LLM...")
    try:
        response = call_llm(
            llm, LLMAdditionalFeedbackResponse, system_prompt, user_prompt
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while calling the LLM: {e}",
        )
    logger.info("Successfully received the response from the LLM")
    return response


def _normalize_for_quote_match(text: str) -> str:
    return re.sub(r"\W+", " ", re.sub(r"-\s*\n\s*", "", text)).casefold().strip()


def _rule_ids_problem(response, expected_rule_ids: list[int]) -> str | None:
    returned = sorted(evaluation.rule_id for evaluation in response.evaluation)
    if returned != expected_rule_ids:
        return f"Expected rule ids {expected_rule_ids}, got {returned}"
    return None


def _invented_quotes_problem(response, normalized_paper: str) -> str | None:
    invented = [
        quote
        for evaluation in response.evaluation
        for quote in evaluation.evidence
        if _normalize_for_quote_match(quote) not in normalized_paper
    ]
    return f"Quotes not found in the paper: {len(invented)}" if invented else None


def request_evaluation(
    db: Session, llm, submission: Submission, rules: list, assignment: Assignment
) -> list[LLMRuleEvaluation]:
    template: PromptTemplate = retrieve_by_purpose(db, "Evaluative")
    feedback_language = (
        retrieve_feedback_language_name(db, assignment.course_id)
        or DEFAULT_FEEDBACK_LANGUAGE
    )
    system_prompt = template.system_text.format(feedback_language=feedback_language)
    normalized_paper = _normalize_for_quote_match(submission.text)

    rules_by_group: dict[int, list] = {}
    for rule in rules:
        rules_by_group.setdefault(rule.rule_group_id, []).append(rule)
    group_calls = [
        (
            sorted(rule.rule_id for rule in group_rules),
            generate_evaluative_user_prompt(
                template, assignment.name, submission.text, group_rules, rules
            ),
        )
        for group_rules in rules_by_group.values()
    ]

    def evaluate_group(group_call) -> list[LLMRuleEvaluation]:
        expected_rule_ids, user_prompt = group_call
        response = call_llm_with_checks(
            llm,
            LLMEvaluationResponse,
            system_prompt,
            user_prompt,
            lambda r: _rule_ids_problem(r, expected_rule_ids),
        )
        quotes_problem = _invented_quotes_problem(response, normalized_paper)
        if quotes_problem:
            logger.warning(quotes_problem)
        return response.evaluation

    logger.info(f"Evaluating {len(rules)} rules in {len(group_calls)} LLM calls...")
    first_call, *remaining_calls = group_calls
    evaluations = list(evaluate_group(first_call))
    if remaining_calls:
        with ThreadPoolExecutor(
            max_workers=min(len(remaining_calls), MAX_PARALLEL_GROUP_CALLS)
        ) as pool:
            for group_evaluations in pool.map(evaluate_group, remaining_calls):
                evaluations.extend(group_evaluations)
    return evaluations


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
    rules: list,
    llm_rule_evaluations: list[LLMRuleEvaluation],
    submission: Submission,
) -> None:
    generate_evaluative_mode_feedbacks_and_fulfillments(
        db, rules, llm_rule_evaluations, submission
    )


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
    logger.info("Successfully updated feedback with additional context")
    rule: Rule = retrieve_rule_by_id(db, feedback.rule_id)
    return InteractiveFeedbackResponse(
        id=feedback.id,
        feedback_text=feedback.feedback_text,
        initially_fulfilled=feedback.initially_fulfilled,
        rule_name=rule.name,
        rule_description=rule.description,
        additional_feedback_text=feedback.additional_text,
        is_valid=feedback.is_valid,
    )


def invalidate_feedback(db: Session, feedback_id: int):
    update_is_valid(db, feedback_id, False)
