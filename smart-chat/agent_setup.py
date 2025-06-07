from langchain.agents import Tool, initialize_agent
from langchain.tools import DuckDuckGoSearchRun
from llm_setup import llm
from dotenv import load_dotenv
import os

load_dotenv()

def create_agent():
    search = DuckDuckGoSearchRun()
    tools = [
        Tool(
            name="duck_search",
            func=search.run,
            description="若無要求，請皆使用繁體中文回答",
        ),
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=os.environ["AGENT_TYPE"],
        verbose=True,
        handle_parsing_errors=True,
    )
    return agent