from fastapi import HTTPException
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from typing import Any, Dict
from sqlalchemy.orm import Session

from ..models.historical_profile import HistoricalProfile
from ..models.prompt_template import PromptTemplate
from ..models.submission import Submission
from ..models.rule import Rule

from .schema import (
    LLMFeedbackResponse,
    LLMAdditionalFeedbackResponse,
    LLMEvaluationResponse,
    LLMUpdatedKnowledge,
    LLMInitialKnowledgeResponse,
)

from ..schemas.submission import TAEvaluationGrade
from ..repository.rule import retrieve_rule_by_feedback_id


def generate_system_prompt(
    historical_profile: HistoricalProfile, prompt_template: PromptTemplate
):
    summary_text = (
        historical_profile.summary
        if historical_profile and historical_profile.summary
        else "Trenutno ne postoji prethodno znanje o ovom studentu."
    )
    system_prompt = prompt_template.system_text.format(student_knowledge=summary_text)
    return system_prompt


def generate_user_prompt_for_initial_student_knowledge_creation(
    prompt_template: PromptTemplate, student_data: Dict[str, Any]
):
    user_prompt = prompt_template.user_text
    for rule in student_data.get("rules"):
        user_prompt += f"Rule name: {rule['rule_name']}, Rule description: {rule['rule_description']}, Grade: {rule['value']}\n"
    return user_prompt


def generate_user_prompt_for_initial_interactive_and_evaluative_mode(
    prompt_template: PromptTemplate,
    knowledge_summarisation_prompt_template: Any,
    rules: list,
    submission: Submission,
):
    user_prompt = prompt_template.user_text
    for _, rule_name, rule_description in rules:
        user_prompt += f"{rule_name}\n{rule_description}\n\n"
    user_prompt += "Tekst:\n"
    user_prompt += submission.text
    if knowledge_summarisation_prompt_template:
        user_prompt += f"\n\n{knowledge_summarisation_prompt_template.user_text}"
    return user_prompt


def construct_evaluative_conclusion_object(
    db: Session,
    ta_evaluation_grades: list[TAEvaluationGrade],
):
    evaluative_conclusion_object = ""
    for ta_evaluation_grade in ta_evaluation_grades:
        rule: Rule = retrieve_rule_by_feedback_id(db, ta_evaluation_grade.feedback_id)
        current_object = f"Naziv pravila: {rule.name}\n\n Opis pravila: {rule.description}\n\n Ocena: {ta_evaluation_grade.final_grade}\n\n Obrazloženje ocene: {ta_evaluation_grade.final_feedback}\n\n"
        evaluative_conclusion_object += current_object

    return evaluative_conclusion_object


def generate_additional_interactive_user_prompt(
    additional_interactive_prompt_template: PromptTemplate,
    knowledge_summarisation_prompt_template: PromptTemplate,
    text: str,
    rule: str,
    feedback: str,
):
    user_prompt = additional_interactive_prompt_template.user_text.format(
        text=text, rule=rule, feedback=feedback
    )
    user_prompt += f"{knowledge_summarisation_prompt_template.user_text}"
    return user_prompt


def generate_evaluative_summarised_knowledge_user_prompt(
    user_prompt_template: str,
    evaluative_conclusion: str,
    latest_historical_profile_summary: str,
):
    user_prompt = user_prompt_template.format(
        summarised_knowledge=latest_historical_profile_summary,
        evaluative_conclusion=evaluative_conclusion,
    )
    return user_prompt


def initialise_format_instructions(pydantic_object_name: str):
    parser = PydanticOutputParser(
        pydantic_object=_initialise_llm_response_schema(pydantic_object_name)
    )
    format_instructions = (
        parser.get_format_instructions().replace("{", "{{").replace("}", "}}")
    )
    return parser, format_instructions


def generate_whole_prompt(format_instructions):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            (
                "user",
                "{user_prompt}\n\n"
                "Vrati podatke u sledećem JSON formatu:\n" + format_instructions,
            ),
        ]
    )
    return prompt


def call_llm(prompt, llm, parser, system_prompt, user_prompt):
    chain = prompt | llm | parser
    response = chain.invoke(
        {"system_prompt": system_prompt, "user_prompt": user_prompt}
    )
    return response


# Extend for each pydantic_object_name
def _initialise_llm_response_schema(pydantic_object_name: str):
    if pydantic_object_name == "LLMFeedbackResponse":
        return LLMFeedbackResponse
    elif pydantic_object_name == "LLMAdditionalFeedbackResponse":
        return LLMAdditionalFeedbackResponse
    elif pydantic_object_name == "LLMEvaluationResponse":
        return LLMEvaluationResponse
    elif pydantic_object_name == "LLMUpdatedKnowledge":
        return LLMUpdatedKnowledge
    elif pydantic_object_name == "LLMInitialKnowledgeResponse":
        return LLMInitialKnowledgeResponse
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Can't initialise LLM response schema, unknown pydantic object name: {pydantic_object_name}",
        )
