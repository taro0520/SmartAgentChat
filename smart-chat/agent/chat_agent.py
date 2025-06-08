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

    若問題內容中包含特定名稱（例如軟體、網站、時間、價格、事件、新聞、教學），
    請務必使用搜尋工具 searxng_search 查詢外部資料。
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