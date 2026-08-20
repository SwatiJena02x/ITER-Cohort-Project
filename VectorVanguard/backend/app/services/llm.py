from langchain_ollama import ChatOllama

from app.core.config import settings


llm = ChatOllama(
    model=settings.OLLAMA_LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0,
)