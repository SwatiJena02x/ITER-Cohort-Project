"""Groq API wrapper for LLM calls.

One LLM call per interaction — no multi-step chains.
Expects structured JSON output with comment, tone, and hint_available.
"""
import json
import os
from groq import Groq

# Valid tones the LLM must return
VALID_TONES = [
    "neutral_thinking",
    "playful_warning",
    "disappointed",
    "impressed",
    "celebrating",
    "encouraging",
]

# Initialize Groq client
_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def _build_analyze_prompt(persona_voice: str, anti_pattern: dict, code: str, optimal_solutions: list[str], previous_comments: list[str]) -> str:
    """Build the prompt for analyze endpoint."""
    optimal_context = ""
    if optimal_solutions:
        sols_formatted = "\n\n".join(optimal_solutions)
        optimal_context = f"\nFor your reference, here are the optimal solutions to this problem:\n{sols_formatted}\nCompare the student's code against these optimal solutions to see if they are on the right track."

    if anti_pattern:
        issue_text = f"The student's code has this logic issue: {anti_pattern['description']}. {anti_pattern['explanation']}."
    else:
        issue_text = "The student is currently typing. Read their ENTIRE code block to understand their approach. Comment dynamically on their specific logic. If they have fatal flaws (e.g. using len() on an integer), point them out. If their code is already optimal and matches the optimal solutions, PRAISE them and do NOT tell them to optimize further."

    prev_comments_text = ""
    if previous_comments:
        prev_list = "\n".join(f"- {c}" for c in previous_comments[-5:])
        prev_comments_text = f"\nYou have ALREADY said these comments (DO NOT repeat any of them, say something completely different):\n{prev_list}"

    return f"""You are a DSA coach. Personality: {persona_voice}
{optimal_context}

{issue_text}

Here is their current code (NOTE: ignore missing indented blocks at the end, they are still typing):
```python
{code}
```
{prev_comments_text}

RULES — VERY IMPORTANT:
- Your comment MUST be 1-2 SHORT sentences only (MAX 25 words total).
- YOU MUST SOUND EXACTLY LIKE THE CHARACTER. Use their catchphrases, tone, and metaphors (e.g. Walter White: 'impure product', 'let him cook', 'chemistry'; Kratos: 'boy', 'warrior'; Thanos: 'balance', 'inevitable').
- Speak PLAINLY and clearly so a beginner can understand the technical advice, but wrap it in the persona's distinct voice.
- Do NOT be boring. Be harsh, witty, or entertaining based on the persona.
- Do NOT explain the solution or name the optimal data structure.
- Do NOT write a paragraph. One punchy line is ideal.
- NEVER repeat yourself. Your response MUST be completely different from your previous comments listed above. Use different words, different sentence structure, different metaphors.

Respond with ONLY this JSON:
{{"comment": "your short comment", "tone": "one_of_valid_tones", "hint_available": true}}

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
    """Generate a 1-2 sentence coach comment based on the AST analysis."""
    import re

    client = _get_client()
    if not client:
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

    # llama-3.3-70b-versatile supports response_format: json_object properly
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=150,
        )
        content = response.choices[0].message.content or ""
        print(f"[LLM] raw_response: {content[:300]}")

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
    """Generate an in-character chat reply."""
    client = _get_client()
    system_prompt = _build_chat_prompt(persona_voice, problem_description, problem_title, rag_context)

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-10:]:  # Keep last 10 messages for context
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.9,
            max_tokens=400,
        )
        return response.choices[0].message.content
    except Exception:
        return "I seem to be momentarily distracted. Ask me again."


def generate_hint_in_character(persona_voice: str, hint_text: str, rag_context: str = "") -> str:
    """Deliver a hint rephrased in the persona's voice."""
    client = _get_client()
    prompt = _build_hint_prompt(persona_voice, hint_text, rag_context)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=60,
        )
        return response.choices[0].message.content
    except Exception:
        return hint_text  # Fall back to raw hint text
