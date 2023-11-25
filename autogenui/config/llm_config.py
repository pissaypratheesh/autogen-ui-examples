import os
from langchain.llms.openai import OpenAI
from langchain.chat_models import AzureChatOpenAI

openai_api_type = os.environ.get("OPENAI_API_TYPE")
openai_api_key = os.environ.get("OPENAI_API_KEY")
serpapi_api_key = os.environ.get("SERPAPI_API_KEY")

def fetch_llm_config():
    if openai_api_type == "azure":
        llm = AzureChatOpenAI(
                openai_api_type="azure",
                openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
                openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_DEPLOYMENT_ID"),
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                temperature=0.7,
                openai_api_version=os.getenv("AZURE_OPENAI_VERSION")
            )
    else:
        llm = OpenAI(temperature=0, openai_api_key=openai_api_key, verbose=True)
    return llm

def fetch_custom(input_str):
    if input_str == "serpapi_api_key":
        return serpapi_api_key
    else:
        return None