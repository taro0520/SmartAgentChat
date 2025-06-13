# Import necessary libraries.
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from agent.chat_agent import get_agent, memory_store
import logging
import os
import glob

# Set up basic logging configuration.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The directory where uploaded files will be stored.
UPLOAD_DIR = "./upload"

# Initialize the FastAPI.
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Store agent instances per user token.
agent_store: Dict[str, object] = {}

# Define the structure of the chat request body.
class ChatRequest(BaseModel):
    token: str
    query: str

# Handle chat message.
@app.post("/api/chat")
def chat(request: ChatRequest) -> Dict[str, str]:
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

# End a chat session and clean up memory and uploaded files.
@app.post("/api/chat/end")
def end_chat(request: ChatRequest) -> Dict[str, str]:
    token = request.token

    # Remove agent and memory.
    agent_store.pop(token, None)
    memory_store.pop(token, None)

    # Delete uploaded files by token.
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

# Handle PDF files upload.
@app.post("/api/chat/upload")
async def upload_pdf(file: UploadFile = File(...), token: str = Form(...)) -> Dict[str, str]:
    filename = f"{token}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"[UPLOAD] Token: {token}, File: {filename}")

    return {"status": "uploaded", "filename": filename}    