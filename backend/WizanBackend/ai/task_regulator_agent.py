import uuid
import google.generativeai as genai

from .task_regulator_tools import (
    check_score,
    get_tasks,
    postpone_task,
    get_tool_declarations,
)
from .task_regulator_limits import apply_limits
from .prompt_builder import build_system_prompt
from .total_score import calculate_total_score
from .memory_manager import save_session_summary, load_past_summaries
from google.api_core.exceptions import ResourceExhausted  # for catching quota errors
from ai.llm import safe_llm_call  # for fallback when quota is hit
BASE_PROMPT = """
You are the Task Regulator Agent for Wizan.
Your job is to look at the user's cognitive score and their tasks,
then decide which tasks are allowed today and which should be postponed.

Always call check_score() first, then get_tasks(), then make decisions.

Rules:
- blocked tasks must be postponed, user cannot override them
- warned tasks should be postponed but user can override
- allowed tasks remain unchanged
"""


TOOLS = {
    "check_score": check_score,
    "get_tasks": get_tasks,
    "postpone_task": postpone_task,
}


def run_task_regulator(user_id, user_message, session_memory, session_id=None):

    # ---------------------------
    # Session ID
    # ---------------------------
    if session_id is None:
        session_id = f"session_{user_id}_{uuid.uuid4().hex[:8]}"

    # ---------------------------
    # Score
    # ---------------------------
    score_data = calculate_total_score(user_id)
    current_score = score_data.get("total_score", 50)

    # ---------------------------
    # Memory injection
    # ---------------------------
    past_summaries = load_past_summaries(user_id, count=3)
    system_prompt = build_system_prompt(BASE_PROMPT, score_data, past_summaries)

    # ---------------------------
    # Gemini model
    # ---------------------------
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        system_instruction=system_prompt,
        tools=get_tool_declarations(),
    )

    # ---------------------------
    # Add user message ONLY
    # ---------------------------
    session_memory.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # ---------------------------
    # Agent loop
    # ---------------------------
    max_iterations = 3

    for _ in range(max_iterations):

       

        try:
            response = model.generate_content(session_memory)

        except ResourceExhausted:
            print("[QUOTA HIT] Switching FULLY to Groq fallback")

            prompt = ""

            for msg in session_memory:
                role = msg.get("role", "")
                for part in msg.get("parts", []):
                    if isinstance(part, dict) and "text" in part:
                        prompt += f"{role}: {part['text']}\n"

            result = safe_llm_call(prompt)

            return {
                "response": result,
                "memory": session_memory,
                "session_id": session_id,
            }
        candidate = response.candidates[0]

        parts = candidate.content.parts or []

        # -----------------------
        # Extract tool calls safely
        # -----------------------
        tool_calls = [
            p for p in parts
            if getattr(p, "function_call", None)
        ]

        # -----------------------
        # NO TOOL CALLS → FINAL ANSWER
        # -----------------------
        if not tool_calls:
            final_text = ""

            for p in parts:
                if getattr(p, "text", None):
                    final_text += p.text

            session_memory.append({
                "role": "model",
                "parts": [{"text": final_text}]
            })

            save_session_summary(user_id, session_id, session_memory)

            return {
                "response": final_text,
                "memory": session_memory,
                "session_id": session_id,
            }

        # -----------------------
        # TOOL EXECUTION
        # -----------------------
        tool_results = []

        for tc in tool_calls:

            fn_name = tc.function_call.name
            fn_args = dict(tc.function_call.args or {})
            fn_args["user_id"] = str(user_id)

            if fn_name not in TOOLS:
                continue

            result = TOOLS[fn_name](**fn_args)

            # apply cognitive limits
            if fn_name == "get_tasks":
                tagged_tasks, limit_message = apply_limits(
                    result,
                    current_score
                )
                result = {
                    "tasks": tagged_tasks,
                    "limit_message": limit_message,
                }

            tool_results.append({
                "function_response": {
                    "name": fn_name,
                    "response": result,
                }
            })

        # -----------------------
        # Safe memory update (IMPORTANT)
        # -----------------------
        session_memory.append({
            "role": "model",
            "parts": [{
                "text": "[TOOL CALL EXECUTED]"
            }]
        })

        session_memory.append({
            "role": "user",
            "parts": tool_results
        })

    # ---------------------------
    # Fallback if loop fails
    # ---------------------------
    save_session_summary(user_id, session_id, session_memory)

    return {
        "response": "Could not complete task regulation.",
        "memory": session_memory,
        "session_id": session_id,
    }
