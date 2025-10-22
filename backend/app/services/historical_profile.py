from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.user import User
from ..models.submission import Submission
from ..models.historical_profile import HistoricalProfile
from ..models.prompt_template import PromptTemplate

from ..utils.logger import logger

from ..repository.historical_profile import retrieve_latest
from ..repository.submission import retrieve_by_id
from ..repository.prompt_template import retrieve_by_purpose

from ..llm.prompt import (
    construct_evaluative_conclusion_object,
    generate_evaluative_summarised_knowledge_user_prompt,
    initialise_format_instructions,
    generate_whole_prompt,
    call_llm,
)
from ..llm.schema import LLMUpdatedKnowledge

from ..schemas.submission import TAEvaluationGradesRequest


def insert_initial_student_historical_profile(
    db: Session, user_id: int, initial_knowledge: str
):
    logger.info(f"Inserting initial historical profile snapshot for user {user_id}...")
    historical_profile = HistoricalProfile(
        user_id=user_id,
        summary=initial_knowledge,
    )
    db.add(historical_profile)
    db.commit()
    logger.info("Successfully inserted initial historical profile snapshot")


def insert_historical_profile_snapshot(
    db: Session, user: User, submission: Submission, updated_knowledge: str
):
    logger.info(f"Inserting historical profile snapshot for user {user.id}...")
    historical_profile = HistoricalProfile(
        user_id=user.id,
        summary=updated_knowledge,
        submission_id=submission.id,
    )
    db.add(historical_profile)
    db.commit()
    logger.info("Successfully inserted historical profile snapshot")


def retrieve_latest_historical_profile_snapshot(db: Session, user: User):
    logger.info(
        f"Retrieving the latest historical profile snapshot for user {user.id}..."
    )
    historical_profile: HistoricalProfile = retrieve_latest(db, user.id)
    logger.info("Successfully retrieved the latest historical profile snapshot")
    return historical_profile


def retrieve_updated_student_knowledge_from_evaluative_mode(
    db: Session, llm, body: TAEvaluationGradesRequest, submission_id: int
) -> LLMUpdatedKnowledge:
    submission: Submission = retrieve_by_id(db, submission_id)
    latest_historical_profile: HistoricalProfile = retrieve_latest(
        db, submission.user_id
    )
    evaluative_conclusion: str = construct_evaluative_conclusion_object(
        db, body.evaluation_grades
    )

    logger.info(
        f"Retrieving knowledge summarisation prompt template for user {submission.user_id}..."
    )
    knowledge_summarisation_prompt_template: PromptTemplate = retrieve_by_purpose(
        db, "Knowledge Summarisation Evaluative"
    )
    logger.info("Successfully retrieved knowledge summarisation prompt template")
    user_prompt = generate_evaluative_summarised_knowledge_user_prompt(
        knowledge_summarisation_prompt_template.user_text,
        evaluative_conclusion,
        latest_historical_profile.summary,
    )
    parser, format_instructions = initialise_format_instructions("LLMUpdatedKnowledge")
    prompt = generate_whole_prompt(format_instructions)
    logger.info("Successfully formed the whole prompt")

    logger.info(f"Calling GPT API... user {submission.user_id}")
    try:
        response = call_llm(
            prompt,
            llm,
            parser,
            knowledge_summarisation_prompt_template.system_text,
            user_prompt,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while calling the GPT API: {e}",
        )
    logger.info("Successfully received the response from the GPT API")
    logger.info(f"Response {response}")
    return response
