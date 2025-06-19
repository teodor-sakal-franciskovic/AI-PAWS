from langchain_openai import ChatOpenAI

from ..settings import settings


def initialise_llm():
    llm = ChatOpenAI(model=settings.llm_name, openai_api_key=settings.openai_api_key)
    return llm
