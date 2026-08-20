"""Shared, traced wrapper around the Ollama chat client."""

import logging
from typing import Any, Dict, Optional

from langsmith import traceable
from ollama import Client

logger = logging.getLogger(__name__)

# Connect to the Ollama container
client = Client(host="http://localhost:11434")

DEFAULT_MODEL = "llama3.2"
DEFAULT_OPTIONS = {"temperature": 0.2}


@traceable(name="ollama_chat", run_type="llm")
def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    options: Optional[Dict[str, Any]] = None,
) -> str:
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options=options or DEFAULT_OPTIONS,
    )
    return response["message"]["content"]
