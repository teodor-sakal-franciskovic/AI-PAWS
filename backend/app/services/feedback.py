from sqlalchemy.orm import Session
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from ..settings import settings

from ..models.submission import Submission
from ..models.prompt_template import PromptTemplate
from ..models.user import User
from ..models.historical_profile import HistoricalProfile

from ..repository.prompt_template import retrieve_by_purpose
from ..repository.historical_profile import retrieve_latest
from ..repository.rule import get_prompt_rules_for_chapter

from ..utils.logger import logger


def request_initial_interactive_feedback(
    db: Session, submission: Submission, user: User, chapter_name: str
):
    initial_interactive_prompt_template: PromptTemplate = retrieve_by_purpose(
        db, "Initial Interactive"
    )
    latest_historical_profile: HistoricalProfile = retrieve_latest(db, user.id)

    rules = get_prompt_rules_for_chapter(db, chapter_name)

    summary_text = (
        latest_historical_profile.summary
        if latest_historical_profile and latest_historical_profile.summary
        else "Trenutno ne postoji prethodno znanje o ovom studentu."
    )
    system_prompt = (initial_interactive_prompt_template.system_text) + summary_text

    user_prompt = initial_interactive_prompt_template.user_text
    for rule_name, rule_description in rules:
        user_prompt += f"{rule_name}\n{rule_description}\n\n"
    user_prompt += "Tekst:\n"
    user_prompt += submission.text

    # logger.info(system_prompt)
    # logger.info("---------")
    # logger.info(user_prompt)

    llm = ChatOpenAI(model="gpt-4o", openai_api_key=settings.openai_api_key)

    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    logger.info(response.content)
    return response.content
    # return GenericResponse(message=f"Response {response.content}", data=None)
