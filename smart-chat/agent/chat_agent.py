from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm_provider import llm

response_prompt = PromptTemplate(
    input_variables=["user_summary", "ai_summary", "query"],
    template="""
    以下是使用者過去的對話摘要：
    {user_summary}

    以下是AI過去的對話摘要：
    {ai_summary}

    使用者目前的提問如下：
    {query}

    請根據上述內容，用繁體中文簡潔明確地回答使用者問題，避免冗詞與重複句。
    若回答包含列表或多點說明，請使用每點一行的清楚格式(可加上\n)，且只需純文字，避免使用markdown語法。
    """
)

use_tool_prompt = PromptTemplate(
    input_variables=["query", "response"],
    template="""
    使用者的問題是：
    {query}

    AI 給的回答是：
    {response}

    請你判斷這個回答是否可信與完整？
    如果 AI 的回答不夠清楚或看起來不知道答案，請回傳 "YES"，表示我們需要讓 Tool Agent 處理。否則回傳 "NO"。
    """
)

def respond_with_summary_context(user_summary: str, ai_summary: str, query: str) -> str:
    chain = LLMChain(llm=llm, prompt=response_prompt)
    return chain.run(user_summary=user_summary, ai_summary=ai_summary, query=query)

def use_tool_agent(query: str, response: str) -> bool:
    chain = LLMChain(llm=llm, prompt=use_tool_prompt)
    result = chain.run(query=query, response=response)
    return "YES" in result