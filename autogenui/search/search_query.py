import os
from langchain.llms.openai import OpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import load_tools, initialize_agent

openai_api_type = os.environ.get("OPENAI_API_TYPE")
openai_api_key = os.environ.get("OPENAI_API_KEY")
serpapi_api_key = os.environ.get("SERPAPI_API_KEY")

def get_search_result(search_term):
    if not serpapi_api_key:
        return ""
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
    tools = load_tools(["serpapi"], llm, serpapi_api_key=serpapi_api_key)
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
    result = agent.run(search_term)
    return result
