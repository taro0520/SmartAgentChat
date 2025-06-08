from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.summarize_agent import generate_summary
from agent.chat_agent import respond_with_summary_context

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

user_message_history = []
ai_message_history = []

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
def chat(request: ChatRequest):
    query = request.query

    # update history
    user_message_history.append(query)
    if len(user_message_history) > 5:
        user_message_history.pop(0)

    # get summary
    user_summary = generate_summary("使用者", user_message_history)
    ai_summary = generate_summary("AI", ai_message_history)

    # send message and get reply
    reply = respond_with_summary_context(user_summary, ai_summary, query)

    ai_message_history.append(reply)
    if len(ai_message_history) > 5:
        ai_message_history.pop(0)
        
    return {"user_summary": user_summary, "ai_summary": ai_summary,"response": reply}
