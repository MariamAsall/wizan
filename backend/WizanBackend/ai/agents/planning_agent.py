"""
planning_agent.py  –  Wizan Planning Agent
Helps the student build a realistic daily/weekly plan based on their
cognitive score. Reads past session history from DB on startup via memory_manager.
"""

from datetime import date

from ai.llm import get_llm
from ai.memory_manager import get_session, save_session
from ai.prompt_builder import build_system_prompt
from ai.prompt_loader import load_prompt

AGENT_NAME = "planning_agent"
MAX_TURNS = 5


def run_planning_agent(
    user_message: str,
    score_data: dict,
    user,
    session_id: str,
) -> str:
    """
    Run one turn of the Planning Agent.

    Args:
        user_message:  The student's input for this turn.
        score_data:    Dict from total_score pipeline:
                         { score, zone, tone, allowed_tasks, ... }
        user:          Django User instance (for DB-scoped memory).
        session_id:    Unique session key, e.g. f"planning_{user.id}".

    Returns:
        The agent's reply as a plain string.
    """

    # ── 1. Load system prompt from YAML ──────────────────────────────────────
    base_prompt = load_prompt(AGENT_NAME)

    system_prompt = build_system_prompt(
        base_prompt,
        {
            **score_data,
            "today": date.today().isoformat(),
            "language": getattr(user, "language", "en"),
        },
    )

    # ── 2. Retrieve past session history from DB (memory on startup) ──────────
    history: list[dict] = get_session(session_id, user=user)
    # history is at most MAX_MESSAGES entries, loaded by memory_manager

    # ── 3. Append the new user message ───────────────────────────────────────
    history.append({"role": "user", "content": user_message})

    # ── 4. Call the LLM ───────────────────────────────────────────────────────
    llm = get_llm()

    # Build the messages list in the format expected by the LLM wrapper
    messages = [{"role": "system", "content": system_prompt}] + history

    reply = ""
    for _ in range(MAX_TURNS):
        response = llm.invoke(messages)

        # Extract text — handle both plain string and object with .content
        reply = response.content if hasattr(response, "content") else str(response)

        # Append the assistant reply to history
        history.append({"role": "model", "content": reply})
        messages.append({"role": "model", "content": reply})

        # Planning agent is conversational — stop after one reply per turn
        break

    # ── 5. Persist updated history back to DB ─────────────────────────────────
    save_session(session_id, history, user=user)

    return reply
