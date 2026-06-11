from ai.llm import get_llm
from ai.prompt_builder import build_system_prompt
import json

BASE_PROMPT = """
You are Wizan's Task Decompose Agent.
Your job is to break down a single task into small manageable steps
based on the student's current cognitive state.

Rules based on tone:
- gentle (score 0-30): max 3 steps, very simple language, short tasks only
- calm (score 31-60): max 5 steps, clear and structured
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
    Takes a task name and score data,
    returns structured steps as a dictionary.
    """

    # Step 1 — build system prompt with cognitive context
    system_prompt = build_system_prompt(BASE_PROMPT, score_data)

    # Step 2 — build user message
    tone = score_data.get("tone", "calm")
    final_score = score_data.get("final_score", 50)

    user_message = f"""
Break down this task into steps: "{task_name}"
Cognitive score: {final_score}/100
Tone: {tone}
Respond with ONLY the JSON object.
"""

    # Step 3 — call the LLM
    llm = get_llm()
    messages = [
        ("system", system_prompt),
        ("human", user_message)
    ]
    response = llm.invoke(messages)

    # Step 4 — parse JSON response
    try:
        raw = response.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
    except json.JSONDecodeError:
        # fallback if AI returns invalid JSON
        result = {
            "steps": [
                {"order": 1, "description": f"Start working on: {task_name}"},
                {"order": 2, "description": "Take a short break"},
                {"order": 3, "description": "Review what you completed"}
            ],
            "tone": tone,
            "estimated_time": 30
        }

    return result