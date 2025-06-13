# Import necessary libraries.
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.memory import CombinedMemory, ConversationBufferMemory, ConversationSummaryMemory
from langchain_community.tools.searx_search.tool import SearxSearchResults
from langchain_community.utilities.searx_search import SearxSearchWrapper
from llm_provider import llm
from typing import Dict
from agent.variable_tool import variable_tool
from agent.pdf_search_tool import search_uploaded_pdf_tool
import os
import logging

# Set up basic logging configuration.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize searx tool with URL from environment variable.
searx_tool = SearxSearchResults(
    wrapper=SearxSearchWrapper(searx_host=os.getenv("SEARXNG_URL"))
)

# Define a custom prompt template for the ReAct agent.
CUSTOM_PROMPT_TEMPLATE = """
You are an AI assistant with access to the following tools:

{tools}

Rules:
- If you know the answer from your own knowledge or conversation history, give the final answer directly.
- Use tools ONLY when you cannot answer confidently.

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

# Create a prompt template instance with the custom ReAct template.
custom_prompt = PromptTemplate(
    input_variables=["input", "chat_history", "agent_scratchpad", "tool_names", "tools"],
    template=CUSTOM_PROMPT_TEMPLATE
)

# Store memory instances per user token.
memory_store: Dict[str, ConversationBufferMemory] = {}

# Initializae an agent by user token.
def get_agent(token: str):
    # Define tools available to the agent.
    TOOLS = [
        search_uploaded_pdf_tool(token),
        Tool(
            name="search",
            func=searx_tool.run,
            description=(
                "Use this tool to search for any kind of information available on the web. "
                "This includes, but is not limited to: details about specific software (features, comparisons, download options), "
                "websites or online platforms (official links, web services), pricing and subscription plans for products or services, "
                "event-related information (dates, schedules, conferences, or competitions), current news or trending topics, "
                "as well as tutorials, guides, or how-to instructions. Use this tool when the user's query requires retrieving "
                "up-to-date information from online sources."
            )
        ),
        variable_tool
    ]

    # Create new memory instance if this token hasn't been seen before.
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
    
    # Initialize and return a LangChain ReAct agent with memory and tools.
    return initialize_agent(
        tools=TOOLS,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )
