# ai/task_decompose_agent.py

from ai.llm import safe_llm_call              # ← changed from get_llm
from ai.prompt_builder import build_system_prompt
import json
from ai.llm import safe_llm_call 
BASE_PROMPT = """
You are Wizan's Task Decompose Agent.
Your job is to break down a single task into small manageable steps
based on the student's current cognitive state.

Rules based on tone:
- gentle  (score 0-30):  max 3 steps, very simple language, short tasks only
- calm    (score 31-60): max 5 steps, clear and structured
- energetic (score 61-100): max 7 steps, detailed and thorough

You MUST respond with ONLY a valid JSON object.
No extra text, no markdown, no backticks.
Follow this exact structure:
{
    "steps": [
        {"order": 1, "description": "..."},
        {"order": 2, "description": "..."}
    ],
    "tone": "gentle|calm|energetic",
    "estimated_time": 30
}
"""


def run_task_decompose_agent(task_name: str, score_data: dict) -> dict:
    """
    Takes a task name and score data.
    Returns structured JSON: steps + tone + estimated_time.
    Makes exactly 1 LLM call.
    """

    # Step 1 — build system prompt with cognitive context
    system_prompt = build_system_prompt(BASE_PROMPT, score_data)

    tone        = score_data.get("tone", "calm")
    final_score = score_data.get("final_score", 50)

    # Step 2 — build the full prompt as one string
    # Why one string? Because safe_llm_call takes a single prompt.
    # We combine system instructions + user request into one clear message.
    full_prompt = f"""{system_prompt}

Task to break down: "{task_name}"
Cognitive score: {final_score}/100
Tone: {tone}
Respond with ONLY the JSON object. No extra text.
"""

    # Step 3 — call LLM safely (Gemini first, Groq fallback on quota)
    raw = safe_llm_call(full_prompt)

    # Step 4 — parse JSON
    # Why try/except? Because even with clear instructions,
    # LLMs occasionally add a sentence before the JSON.
    # The fallback gives the user a basic plan instead of a crash.
    try:
        cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        result = {
            "steps": [
                {"order": 1, "description": f"Start working on: {task_name}"},
                {"order": 2, "description": "Take a short break"},
                {"order": 3, "description": "Review what you completed"}
            ],
            "tone":           tone,
            "estimated_time": 30
        }

    return result