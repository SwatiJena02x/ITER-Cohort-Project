"""
llm/langchain_config.py
--------------------------
Configures the LangChain LLM client used by the risk-scoring agent to turn
structured evidence into a human-readable explanation/report.

Defaults to a local Ollama model (see OLLAMA_MODEL in .env) so the project
runs without any paid API key. Swap `get_llm()` to point at another
LangChain-compatible chat model (OpenAI, Anthropic, etc.) if you prefer.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_llm = None  # lazy singleton


def get_llm():
    """
    Returns a LangChain chat-model instance. Falls back to a deterministic
    offline stub (see llm/prompts.py: `render_fallback_summary`) if no LLM
    backend is reachable, so the pipeline never hard-fails on a missing model.
    """
    global _llm
    if _llm is not None:
        return _llm

    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
            import socket

            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            if "://ollama:" in ollama_url or "://ollama" in ollama_url:
                try:
                    socket.gethostbyname("ollama")
                except Exception:
                    ollama_url = ollama_url.replace("://ollama:", "://localhost:").replace("://ollama", "://localhost")

            _llm = ChatOllama(
                base_url=ollama_url,
                model=os.getenv("OLLAMA_MODEL", "llama3"),
                temperature=0.2,
                request_timeout=3.0,
            )
            return _llm
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not initialise Ollama LLM (%s). Falling back to offline summary.", exc)
            return None

    logger.warning("Unknown LLM_PROVIDER=%s. Falling back to offline summary.", provider)
    return None

