from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.summarize_agent import generate_summary
from agent.chat_agent import respond_with_summary_context
from typing import Dict, List
import uuid
import json
import os

DATA_FILE = "chat_history.json"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# user_histories: Dict[str, List[str]] = {}
# ai_histories: Dict[str, List[str]] = {}

def load_histories():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"user": {}, "ai": {}}

def save_histories(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

chat_data = load_histories()
user_histories = chat_data["user"]
ai_histories = chat_data["ai"]

class ChatRequest(BaseModel):
    token: str
    query: str

@app.post("/api/chat")
def chat(request: ChatRequest):
    token = request.token
    query = request.query

    if token not in user_histories:
        user_histories[token] = []
    if token not in ai_histories:
        ai_histories[token] = []

    # update history
    user_histories[token].append(query)
    if len(user_histories[token]) > 5:
        user_histories[token].pop(0)

    # get summary
    user_summary = generate_summary("使用者", user_histories[token])
    ai_summary = generate_summary("AI", ai_histories[token])

    # send message and get reply
    reply = respond_with_summary_context(user_summary, ai_summary, query)

    ai_histories[token].append(reply)
    if len(ai_histories[token]) > 5:
        ai_histories[token].pop(0)
    
    save_histories({"user": user_histories, "ai": ai_histories})

    return {"user_summary": user_summary, "ai_summary": ai_summary,"response": reply, "token": token}

@app.post("/api/chat/end")
def end_chat(request: ChatRequest):
    token = request.token
    user_histories.pop(token, None)
    ai_histories.pop(token, None)
    return {"status": "ended"}

