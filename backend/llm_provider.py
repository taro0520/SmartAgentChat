from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.environ["GEMINI_MODEL"],
    temperature=0.7,
    max_output_tokens=300,
    google_api_key=os.environ["GEMINI_API_KEY"],
)