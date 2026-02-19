from langchain_openai import AzureChatOpenAI
from ..settings import settings


def initialise_llm():
    llm = AzureChatOpenAI(
        azure_endpoint="https://galton.openai.azure.com/",
        api_key=settings.openai_api_key,
        api_version="2024-12-01-preview",
        deployment_name="gpt-4o",
        temperature=0,
        top_p=1,
    )
    return llm
