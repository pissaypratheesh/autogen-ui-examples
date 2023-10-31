import os
from langchain.llms.openai import OpenAI
from langchain.agents import load_tools, initialize_agent
openai_api_key = os.environ.get("OPENAI_API_KEY")
serpapi_api_key = os.environ.get("SERPAPI_API_KEY")

def get_search_result(search_term):
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key, verbose=True)
    tools = load_tools(["serpapi"], llm, serpapi_api_key=serpapi_api_key)
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
    result = agent.run(search_term)
    return result
