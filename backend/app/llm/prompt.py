from typing import Any, Dict

from pydantic import ValidationError

from ..models.historical_profile import HistoricalProfile
from ..models.prompt_template import PromptTemplate
from ..models.submission import Submission
from ..settings import settings
from ..utils.logger import logger

LLM_MAX_TOKENS = 16000
LLM_EFFORT = "medium"
LLM_FALLBACK_BETA = "server-side-fallback-2026-07-01"
MAX_LLM_ATTEMPTS = 3


class LLMRefusalError(Exception):
    pass


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
    chapter_name: str,
):
    user_prompt = prompt_template.user_text
    for _, rule_name, rule_description in rules:
        user_prompt += f"{rule_name}\n{rule_description}\n\n"
    user_prompt += f"Evaluiraj SAMO deo teksta koji se odnosi na poglavlje {chapter_name}. Ostatak teksta koristi kao dodatni kontekst.\n"
    user_prompt += "Tekst:\n"
    user_prompt += submission.text
    if knowledge_summarisation_prompt_template:
        user_prompt += f"\n\n{knowledge_summarisation_prompt_template.user_text}"
    return user_prompt


def generate_evaluative_user_prompt(
    prompt_template: PromptTemplate,
    assignment_name: str,
    paper_text: str,
    rules: list,
    all_rules: list,
):
    rule_group_criteria = "\n".join(
        f'<rule id="{rule.rule_id}" name="{rule.rule_name}">\n{rule.rule_description}\n</rule>'
        for rule in rules
    )
    shared_text, closing_text = prompt_template.user_text.split("{rule_group_criteria}")
    return [
        {
            "type": "text",
            "text": shared_text.format(
                assignment_name=assignment_name,
                paper_text=paper_text.replace("</paper>", ""),
                all_rules="\n".join(
                    f"- {rule.rule_name}: {rule.user_description or ''}"
                    for rule in all_rules
                ),
            ),
            "cache_control": {"type": "ephemeral"},
        },
        {"type": "text", "text": rule_group_criteria + closing_text},
    ]


def generate_rule_compilation_user_prompt(
    prompt_template: PromptTemplate,
    rule_group_name: str,
    rules_to_process: list,
    other_rules: list,
):
    def render(rules: list) -> str:
        return (
            "\n".join(
                f"- id {rule.id}, {rule.name}: {rule.user_description or ''}"
                for rule in rules
            )
            or "None"
        )

    return prompt_template.user_text.format(
        rule_group_name=rule_group_name,
        rules_to_process=render(rules_to_process),
        other_rules=render(other_rules),
    )


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


def call_llm(llm, response_schema, system_prompt, user_prompt):
    with llm.beta.messages.stream(
        model=settings.llm_name,
        max_tokens=LLM_MAX_TOKENS,
        betas=[LLM_FALLBACK_BETA],
        fallbacks="default",
        output_config={"effort": LLM_EFFORT},
        output_format=response_schema,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        message = stream.get_final_message()
    usage = message.usage
    logger.info(
        f"LLM usage: {usage.input_tokens} uncached input tokens, "
        f"{usage.cache_creation_input_tokens} written to cache, "
        f"{usage.cache_read_input_tokens} read from cache, "
        f"{usage.output_tokens} output tokens"
    )
    if any(block.type == "fallback" for block in message.content):
        logger.warning(f"The LLM request was answered by a fallback model: {message.model}")
    if message.stop_reason == "refusal":
        raise LLMRefusalError(f"The LLM declined the request: {message.stop_details}")
    if message.parsed_output is None:
        raise ValueError(f"The LLM returned no output, stop reason: {message.stop_reason}")
    return message.parsed_output


def call_llm_with_checks(llm, response_schema, system_prompt, user_prompt, required_check):
    problem = None
    for attempt in range(1, MAX_LLM_ATTEMPTS + 1):
        try:
            response = call_llm(llm, response_schema, system_prompt, user_prompt)
        except LLMRefusalError:
            raise
        except Exception as e:
            problem = (
                e.errors(include_url=False, include_input=False)
                if isinstance(e, ValidationError)
                else str(e)
            )
            logger.warning(f"LLM attempt {attempt} failed: {problem}")
            continue
        problem = required_check(response)
        if not problem:
            return response
        logger.warning(f"LLM attempt {attempt} rejected: {problem}")
    raise RuntimeError(
        f"LLM response still invalid after {MAX_LLM_ATTEMPTS} attempts: {problem}"
    )
