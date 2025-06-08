import os
import requests
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from llm_provider import llm

load_dotenv()

def searxng_search(query: str) -> str:
    try:
        url = os.environ["SEARXNG_URL"],
        params = {
            "q": query,
            "format": "json",
            "categories": "general",
            "safesearch": 1,
            "engines": "google",
            "limit": 5,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return "找不到相關結果。"
        
        output = []
        for r in results[:5]:
            title = r.get("title", "無標題")
            url = r.get("url", "")
            output.append(f"{title}\n{url}")
        return "\n\n".join(output)
    except Exception as e:
        return f"SearxNG 搜尋失敗：{str(e)}"

def create_react_agent():
    tools = [
        Tool(
            name="searxng_search",
            func=searxng_search,
            description="當你不確定答案、或使用者問的是最新資訊、網頁、教學、價格等，請使用此工具查詢（請用繁體中文回覆）",
        )
    ]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type="react-description",
        verbose=True,
        handle_parsing_errors=True,
        memory=memory,
    )

    return agent
