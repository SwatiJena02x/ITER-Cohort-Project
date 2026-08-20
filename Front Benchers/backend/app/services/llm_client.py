"""LangChain + Groq LLM wrapper for DSA Coach.

Uses ChatGroq from langchain-groq for all LLM interactions.
Model: openai/gpt-oss-120b (Groq LPU inference).
One LLM call per interaction — no multi-step chains.
Expects structured JSON output with comment, tone, and hint_available for analyze.
"""
import json
import os
import re
from typing import Optional

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Valid tones the LLM must return
VALID_TONES = [
    "neutral_thinking",
    "playful_warning",
    "disappointed",
    "impressed",
    "celebrating",
    "encouraging",
]

# ─── Model configuration ───────────────────────────────────────────────
MODEL_NAME = "openai/gpt-oss-120b"

# Initialize LangChain ChatGroq client
_llm: Optional[ChatGroq] = None


def _get_llm() -> ChatGroq:
    """Get or create the ChatGroq LLM instance."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=MODEL_NAME,
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7,
        )
    return _llm


def _build_analyze_prompt(persona_voice: str, anti_pattern: dict, code: str, optimal_solutions: list[str], previous_comments: list[str]) -> str:
    """Build the prompt for analyze endpoint."""
    optimal_context = ""
    if optimal_solutions:
        sols_formatted = "\n\n".join(optimal_solutions)
        optimal_context = f"\nFor your reference, here are the optimal solutions to this problem:\n{sols_formatted}\nCompare the student's code against these optimal solutions to see if they are on the right track."

    if anti_pattern:
        issue_text = f"The student's code has a logic issue: {anti_pattern['description']}. {anti_pattern['explanation']}."
    else:
        issue_text = "The student is currently typing. Their code might be incomplete. Do NOT be disappointed just because they haven't finished typing (e.g. missing returns). If they are on the right track towards the optimal solution, use a 'neutral_thinking' or 'encouraging' tone. ONLY use 'disappointed' if they are doing something fundamentally wrong. If their code is perfectly optimal and complete, PRAISE them with 'impressed'."

    prev_comments_text = ""
    if previous_comments:
        prev_list = "\n".join(f"- {c}" for c in previous_comments[-5:])
        prev_comments_text = f"\nYou have ALREADY said these comments (DO NOT repeat them):\n{prev_list}"

    return f"""You are a DSA coach. Personality: {persona_voice}
{optimal_context}

{issue_text}

Here is their current code:
```python
{code}
```
{prev_comments_text}

RULES — VERY IMPORTANT:
- Your comment MUST be EXACTLY ONE short, punchy sentence (MAX 15 words).
- YOU MUST SOUND EXACTLY LIKE THE CHARACTER. Use their catchphrases, tone, and metaphors.
- Speak PLAINLY and clearly so a beginner can understand.
- Do NOT explain the entire solution or name the exact data structure to use.
- NEVER repeat yourself. Your response MUST be completely different from previous comments.

Respond with ONLY this JSON:
{{"comment": "your 1-sentence comment", "tone": "one_of_valid_tones", "hint_available": true}}

Valid tones: {', '.join(VALID_TONES)}"""


def _build_chat_prompt(persona_voice: str, problem_description: str, problem_title: str, rag_context: str = "") -> str:
    """Build the system prompt for chat endpoint."""
    rag_section = ""
    if rag_context:
        rag_section = f"\nRelevant DSA knowledge to help answer the student's question:\n{rag_context}"

    return f"""You are a DSA coach. Personality: {persona_voice}

Problem: "{problem_title}" — {problem_description}
{rag_section}

RULES:
- You are allowed to explain DSA concepts if the student asks, but keep it concise (2-4 sentences max).
- If the 'Relevant DSA knowledge' is directly relevant to the current problem and their actual question, USE IT to explain the concept in your own character's voice.
- If a retrieved chunk describes a different problem, a different variant, or an unrelated technique, IGNORE IT COMPLETELY rather than forcing it into the answer.
- Speak PLAINLY and clearly so a beginner can understand.
- Stay firmly in character. Use their metaphors and tone.
- Guide them towards the solution, but don't just write the code for them.
- VERY IMPORTANT: Keep your response under 60 words. You MUST finish your final sentence completely. Do not trail off or get cut off!"""


def _build_hint_prompt(persona_voice: str, hint_text: str, rag_context: str = "") -> str:
    """Build the prompt for delivering a hint in character."""
    rag_section = ""
    if rag_context:
        rag_section = f"\nRelevant DSA knowledge for context:\n{rag_context}"

    return f"""Personality: {persona_voice}
{rag_section}

Rephrase this hint in character in ONE short sentence (max 20 words). Speak PLAINLY and clearly so a beginner can understand. Keep the technical content intact:
"{hint_text}"

Respond with ONLY the rephrased hint. No quotes, no JSON, no extra text."""


def generate_analyze_comment(
    persona_voice: str,
    anti_pattern: dict,
    code: str,
    optimal_solutions: list[str],
    previous_comments: list[str] = [],
) -> dict:
    """Generate a 1-2 sentence coach comment based on the AST analysis.
    
    Uses LangChain ChatGroq. JSON is extracted from the text response
    using our robust _extract_json parser.
    """
    llm = _get_llm()
    if not os.getenv("GROQ_API_KEY"):
        return {"comment": "[Groq API key missing] Please set GROQ_API_KEY in .env", "tone": "neutral_thinking", "hint_available": False}

    prompt = _build_analyze_prompt(persona_voice, anti_pattern, code, optimal_solutions, previous_comments)

    def _extract_json(text: str) -> dict:
        """Extract JSON from LLM output, even if wrapped in extra text."""
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try to find JSON object in the text
        match = re.search(r'\{[^{}]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}

    def _validate(result: dict) -> dict:
        if result.get("tone") not in VALID_TONES:
            result["tone"] = "playful_warning"
        result.setdefault("hint_available", True)
        result.setdefault("comment", "Keep going...")
        return result

    try:
        # LangChain invoke — JSON mode requires a user message alongside the system prompt
        response = llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content="Analyze the code and respond with the JSON."),
            ],
        )
        content = response.content or ""
        print(f"[LLM Analyze] raw_response: {content.encode('utf-8', errors='replace').decode('utf-8')[:300]}")

        result = _extract_json(content)
        if result.get("comment"):
            return _validate(result)
        
        # If JSON extraction failed, use the text itself as the comment
        if content.strip():
            return _validate({"comment": content.strip()[:120], "tone": "playful_warning", "hint_available": True})

    except Exception as e:
        print(f"[LLM] error: {e}")

    return {
        "comment": "Hmm, let me take another look at that code...",
        "tone": "neutral_thinking",
        "hint_available": True,
    }


def generate_chat_reply(
    persona_voice: str,
    problem_description: str,
    problem_title: str,
    message: str,
    history: list[dict],
    rag_context: str = "",
) -> str:
    """Generate an in-character chat reply using LangChain ChatGroq."""
    llm = _get_llm()
    system_prompt = _build_chat_prompt(persona_voice, problem_description, problem_title, rag_context)

    # Build LangChain message list from chat history
    messages = [SystemMessage(content=system_prompt)]
    for msg in history[-10:]:  # Keep last 10 messages for context
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=message))

    try:
        response = llm.invoke(
            messages,
            max_tokens=400,
            temperature=0.9,
        )
        return response.content
    except Exception as e:
        print(f"[LLM Error] generate_chat_reply failed: {e}")
        return "I seem to be momentarily distracted. Ask me again."


def generate_hint_in_character(persona_voice: str, hint_text: str, rag_context: str = "") -> str:
    """Deliver a hint rephrased in the persona's voice using LangChain ChatGroq."""
    llm = _get_llm()
    prompt = _build_hint_prompt(persona_voice, hint_text, rag_context)

    try:
        response = llm.invoke(
            [HumanMessage(content=prompt)],
            temperature=0.8,
        )
        content = response.content or ""
        print(f"[LLM Hint] raw_response: {content.encode('utf-8', errors='replace').decode('utf-8')[:300]}")
        return content
    except Exception as e:
        print(f"[LLM Error] generate_hint_in_character failed: {e}")
        return hint_text  # Fall back to raw hint text
