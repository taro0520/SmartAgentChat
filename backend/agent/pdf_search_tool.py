# Import necessary libraries.
import os
from typing import List, Callable
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.agents import Tool
from llm_provider import llm

# The directory where uploaded files will be stored.
PDF_DIR = "./upload"

# Handle PDF search function.
class PDFSearchManager:
    def __init__(self):
        # Load embedding model for converting text to vectors.
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Get all PDF files uploaded by the user with this token.
    def get_user_pdfs(self, token: str) -> List[str]:
        return [os.path.join(PDF_DIR, f) for f in os.listdir(PDF_DIR)
                if f.startswith(f"{token}_") and f.endswith(".pdf")]

    # Load and parse the documents from filepaths into LangChain document objects.
    def load_documents(self, filepaths: List[str]):
        docs = []
        for path in filepaths:
            loader = PyMuPDFLoader(path)
            docs.extend(loader.load())
        return docs

    # Perform semantic search over user's uploaded PDFs using vector similarity.
    def search(self, query: str, token: str) -> str:
        pdf_paths = self.get_user_pdfs(token)
        if not pdf_paths:
            return f"No PDFs found for token: {token}"

        docs = self.load_documents(pdf_paths)
        if not docs:
            return f"Failed to load any content from PDFs for token: {token}"

        # Split documents into chunks to create embeddings.
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        # Create vectorstore and retriever using similarity search.
        vectorstore = Chroma.from_documents(chunks, self.embedding_model)
        retriever = vectorstore.as_retriever(search_type="similarity", k=3)

        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        try:
            answer = qa.run(query)
            return answer.strip()
        except Exception as e:
            return f"Error while searching PDFs: {str(e)}"

pdf_search_manager = PDFSearchManager()

# Define a LangChain tool for use in agents, wrapping the PDF search
def search_uploaded_pdf_tool(token: str) -> Tool:
    def search_func(query: str) -> str:
        return pdf_search_manager.search(query, token)

    return Tool(
        name="search_uploaded_pdf",
        func=search_func,
        description=(
            "Use this tool to search inside user's uploaded PDF files for any questions, "
            "including requests for outlines, summaries, or specific content in the PDFs."
        )
    )
