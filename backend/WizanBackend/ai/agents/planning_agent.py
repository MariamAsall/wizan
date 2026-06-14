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

from ai.llm import safe_llm_call  # Changed import


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
    """

    # ── 1. Load and Format system prompt from YAML ───────────────────────────
    # load_prompt returns a dictionary parsed from the YAML file
    yaml_data = load_prompt(AGENT_NAME)
    
    # Extract the raw string template waiting for variable formatting
    raw_template = yaml_data.get("system_prompt", "")
    
    # Format the template placeholders ({score}, {zone}, etc.)
    # We map both formats (e.g., score vs final_score) so it's robust
    formatted_base_prompt = raw_template.format(
        score=score_data.get("score", score_data.get("final_score", 50)),
        zone=score_data.get("zone", "MEDIUM"),
        tone=score_data.get("tone", "calm"),
        allowed_tasks=score_data.get("allowed_tasks", 3),
        today=date.today().isoformat(),
        language=getattr(user, "language", "en"),
    )

    # Now we pass a clean string to build_system_prompt
    system_prompt = build_system_prompt(
        base_prompt=formatted_base_prompt,
        score_data={
            **score_data,
            # Ensure prompt_builder gets the exact key names it expects as well
            "final_score": score_data.get("final_score", score_data.get("score", 50)),
            "label": score_data.get("label", f"{score_data.get('zone', 'Medium')} Cognitive Load"),
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


    reply = safe_llm_call(messages)
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
