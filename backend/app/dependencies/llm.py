import anthropic

from ..settings import settings


def initialise_llm():
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)
