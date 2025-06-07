from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_setup import llm
from agent_setup import create_agent
from langchain.chains import RetrievalQA

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
    allow_credentials = True,
)

class ChatRequest(BaseModel):
    query : str

def run_agent(query):
    agent = create_agent()
    return agent.run(query)

@app.post("/api/chat")
def chat(request : ChatRequest):
    query = request.query
    reply = run_agent(query)
    return {"response" : reply}
