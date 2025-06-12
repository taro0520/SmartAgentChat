from langchain.agents import Tool, initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.memory import CombinedMemory, ConversationBufferMemory, ConversationSummaryMemory
from langchain_community.tools.searx_search.tool import SearxSearchResults
from langchain_community.utilities.searx_search import SearxSearchWrapper
from llm_provider import llm
from typing import Dict
from agent.tool_agent import variable_tool
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

searx_tool = SearxSearchResults(
    wrapper=SearxSearchWrapper(searx_host=os.getenv("SEARXNG_URL"))
)

TOOLS = [
    Tool(
        name="search_software",
        func=searx_tool.run,
        description="Use this tool when the user asks about specific software, its features, download options, or comparisons."
    ),
    Tool(
        name="search_website",
        func=searx_tool.run,
        description="Use this tool when the user mentions a website, platform, web service, or needs to find a web page or official link."
    ),
    Tool(
        name="search_date_time",
        func=searx_tool.run,
        description="Use this tool when the user asks about specific dates, schedules, timelines, or time-related details of an event or service."
    ),
    Tool(
        name="search_price",
        func=searx_tool.run,
        description="Use this tool when the user inquires about pricing, subscription plans, product costs, or any fee-related information."
    ),
    Tool(
        name="search_event",
        func=searx_tool.run,
        description="Use this tool when the user asks about events, conferences, talks, competitions, or other happenings."
    ),
    Tool(
        name="search_news",
        func=searx_tool.run,
        description="Use this tool when the user asks about current news, trending topics, updates, or public announcements."
    ),
    Tool(
        name="search_tutorial",
        func=searx_tool.run,
        description="Use this tool when the user requests tutorials, how-to guides, step-by-step instructions, or learning resources."
    ),
    variable_tool
]

CUSTOM_PROMPT_TEMPLATE = """
You are an AI assistant with access to the following tools:

{tools}

Rules:
- If you know the answer from your own knowledge or conversation history, give the final answer directly.
- Use tools ONLY when you cannot answer confidently.
- Use 'ask_for_clarification' tool ONLY if the user input is ambiguous or incomplete.

When you respond, ONLY use one of the following formats:

Thought: <your reasoning about the next step>
Action: <tool name>
Action Input: <input for the tool>

OR

Final Answer: <your final answer>

Conversation so far:
{chat_history}

User input:
{input}

Thought:
"""

custom_prompt = PromptTemplate(
    input_variables=["input", "chat_history", "agent_scratchpad", "tool_names", "tools"],
    template=CUSTOM_PROMPT_TEMPLATE
)

memory_store: Dict[str, ConversationBufferMemory] = {}

def get_agent(token: str):
    if token not in memory_store:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=InMemoryChatMessageHistory(),
        )
        memory_store[token] = memory
        logger.info(f"[MEMORY] Created new memory for token: {token}, Memory ID: {id(memory)}")
    else:
        memory = memory_store[token]
        logger.info(f"[MEMORY] Reused memory for token: {token}, Memory ID: {id(memory)}")

    logger.info(f"[MEMORY DETAIL] ChatMemory ID: {id(memory.chat_memory)}")
    return initialize_agent(
        tools=TOOLS,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )
