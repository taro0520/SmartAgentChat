from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from agent.chat_agent import get_agent, memory_store
import logging
import os
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
UPLOAD_DIR = "./upload"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

agent_store: Dict[str, object] = {}

class ChatRequest(BaseModel):
    token: str
    query: str

@app.post("/api/chat")
def chat(request: ChatRequest):
    token = request.token
    query = request.query

    logger.info(f"[REQUEST] Token: {token}, Query: {query}")

    if token not in agent_store:
        logger.info(f"[AGENT] New agent created for token: {token}")

        agent_store[token] = get_agent(token)

    agent = agent_store[token]
    result = agent.invoke({"input": query})
    reply = result["output"]

    logger.info(f"[RESPONSE] Token: {token}, Reply: {reply}")

    return {"response": reply, "token": token}

@app.post("/api/chat/end")
def end_chat(request: ChatRequest):
    token = request.token
    agent_store.pop(token, None)
    memory_store.pop(token, None)

    deleted_files = []
    pattern = os.path.join(UPLOAD_DIR, f"{token}_*")

    for file_path in glob.glob(pattern):
        try:
            os.remove(file_path)
            deleted_files.append(os.path.basename(file_path))
        except Exception as e:
            logger.error(f"[DELETE FAILED] {file_path}: {e}")
    
    logger.info(f"[SESSION ENDED] Token: {token}, Deleted Files: {deleted_files}")

    return {"status": "ended"}

@app.post("/api/chat/upload")
async def upload_pdf(file: UploadFile = File(...), token: str = Form(...)):
    filename = f"{token}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"[UPLOAD] Token: {token}, File: {filename}")

    return {"status": "uploaded", "filename": filename}    