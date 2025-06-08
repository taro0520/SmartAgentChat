from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm_provider import llm
from agent.tool_agent import create_react_agent

response_prompt = PromptTemplate(
    input_variables=["user_summary", "ai_summary", "query"],
    template="""
    以下是使用者過去的對話摘要：
    {user_summary}

    以下是AI過去的對話摘要：
    {ai_summary}

    使用者目前的提問如下：
    {query}

    請根據上述內容，請你判斷是否需要使用搜尋工具，若需要，請呼叫工具取得資訊，
    最後綜合回答使用者問題，請用繁體中文回覆。
    """
)

def respond_with_summary_context(user_summary: str, ai_summary: str, query: str) -> str:
    agent = create_react_agent()

    prompt_input = response_prompt.format(
        user_summary=user_summary,
        ai_summary=ai_summary,
        query=query,
    )

    return agent.run(prompt_input)