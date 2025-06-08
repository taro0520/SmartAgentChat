import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
from llm_provider import llm

load_dotenv()

def create_tool_agent():
    search = DuckDuckGoSearchRun()
    tools = [
        Tool(
            name="duck_search",
            func=search.run,
            description="使用 DuckDuckGo 搜尋資訊（請以繁體中文回覆）",
        )
    ]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=os.environ["AGENT_TYPE"],
        verbose=True,
        handle_parsing_errors=True,
        memory=memory,
    )

    return agent
