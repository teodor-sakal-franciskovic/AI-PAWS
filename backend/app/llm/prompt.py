from fastapi import HTTPException
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

from ..models.historical_profile import HistoricalProfile
from ..models.prompt_template import PromptTemplate
from ..models.submission import Submission
from .schema import LLMFeedbackResponse, LLMAdditionalFeedbackResponse


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


def generate_initial_interactive_user_prompt(
    initial_interactive_prompt_template: PromptTemplate,
    knowledge_summarisation_prompt_template: PromptTemplate,
    rules: list,
    submission: Submission,
):
    user_prompt = initial_interactive_prompt_template.user_text
    for _, rule_name, rule_description in rules:
        user_prompt += f"{rule_name}\n{rule_description}\n\n"
    user_prompt += "Tekst:\n"
    user_prompt += submission.text
    user_prompt += f"\n\n{knowledge_summarisation_prompt_template.user_text}"
    return user_prompt


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


def call_prompt(prompt, llm, parser, system_prompt, user_prompt):
    chain = prompt | llm | parser
    response = chain.invoke(
        {"system_prompt": system_prompt, "user_prompt": user_prompt}
    )
    return response


# TODO: Extend for each pydantic_object_name
def _initialise_llm_response_schema(pydantic_object_name: str):
    if pydantic_object_name == "LLMFeedbackResponse":
        return LLMFeedbackResponse
    elif pydantic_object_name == "LLMAdditionalFeedbackResponse":
        return LLMAdditionalFeedbackResponse
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Can't initialise LLM response schema, unknown pydantic object name: {pydantic_object_name}",
        )
