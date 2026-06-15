# from ai.models import AgentMemory

# def save_session_summary(user_id, session_id, conversation_history):
#     """
#     Called at the END of every session.
#     Sends the conversation to Gemini, gets a summary, saves to DB.
#     """
#     import google.generativeai as genai

#     # Build a readable transcript from the history list
#     transcript = ""
#     for turn in conversation_history:
#         role = turn["role"]
#         for part in turn["parts"]:
#             if isinstance(part, dict) and "text" in part:
#                 transcript += f"{role}: {part['text']}\n"

#     if not transcript.strip():
#         return  # nothing to summarize

#     model = genai.GenerativeModel("gemini-2.0-flash")
#     prompt = f"""
# Summarize this conversation in 2-3 lines maximum.
# Focus on: what tasks were allowed, what was postponed, and how the user felt.
# Be factual and brief.

# Conversation:
# {transcript}
# """
#     response = model.generate_content(prompt)
#     summary_text = response.text.strip()

#     AgentMemory.objects.create(
#         user_id=user_id,
#         session_id=session_id,
#         summary=summary_text
#     )


# def load_past_summaries(user_id, count=3):
#     """
#     Called at the START of every session.
#     Returns the last N session summaries as a single string.
#     """
#     records = AgentMemory.objects.filter(
#         user_id=user_id
#     ).order_by('-created_at')[:count]

#     if not records:
#         return ""

#     lines = []
#     for i, record in enumerate(reversed(records), 1):
#         lines.append(f"Session {i} ({record.created_at.date()}): {record.summary}")

#     return "\n".join(lines)

# ai/memory_manager.py

from ai.models import AgentMemory
from ai.llm import safe_llm_call    # ← the only new import


def save_session_summary(user_id, session_id, conversation_history):
    """
    Called at the END of every session.
    Why? So the next session the agent remembers what happened before.
    """

    # Step 1 — build a readable transcript from the conversation history
    # Why? Because Gemini needs plain text, not a Python list of dicts
    transcript = ""
    for turn in conversation_history:
        role = turn["role"]
        for part in turn["parts"]:
            if isinstance(part, dict) and "text" in part:
                transcript += f"{role}: {part['text']}\n"

    # Step 2 — if the session had no text at all, skip silently
    if not transcript.strip():
        return

    # Step 3 — ask the LLM to summarize
    # Why safe_llm_call instead of genai directly?
    # Because safe_llm_call tries Gemini first, and if quota is hit
    # it automatically switches to Groq — no crash, no lost summary
    prompt = f"""
Summarize this conversation in 2-3 lines maximum.
Focus on: what tasks were allowed, what was postponed, and how the user felt.
Be factual and brief.

Conversation:
{transcript}
"""
    summary_text = safe_llm_call(prompt)    # ← was: model.generate_content(prompt)

    # Step 4 — save to DB
    AgentMemory.objects.create(
        user_id=user_id,
        session_id=session_id,
        summary=summary_text.strip()
    )


def load_past_summaries(user_id, count=3):
    """
    Called at the START of every session.
    Returns the last N summaries as one string injected into the system prompt.
    Why 3? Enough history for the agent to notice patterns without overloading the prompt.
    """
    records = AgentMemory.objects.filter(
        user_id=user_id
    ).order_by('-created_at')[:count]

    # First time user — no history yet, return empty string safely
    if not records:
        return ""

    lines = []
    for i, record in enumerate(reversed(records), 1):
        lines.append(f"Session {i} ({record.created_at.date()}): {record.summary}")

    return "\n".join(lines)


# ADD to the bottom of ai/memory_manager.py
# (keep everything above exactly as it is)

import json
from ai.models import AgentSession   # make sure this model exists in ai/models.py

MAX_MESSAGES = 20  # keep last 20 turns — older ones already summarized

def get_session(session_id: str, user=None) -> list:
    """
    Load conversation turns for this session from DB.
    Why DB instead of RAM? So history survives server restarts.
    Returns empty list if session doesn't exist yet — safe for first turn.
    """
    try:
        record = AgentSession.objects.get(session_id=session_id)
        return json.loads(record.history)
    except AgentSession.DoesNotExist:
        return []   # first time — no history yet


def save_session(session_id: str, history: list, user=None) -> None:
    """
    Save updated conversation turns back to DB.
    Why update_or_create? Because we don't know if this session
    already exists or is being created for the first time.
    Why trim to MAX_MESSAGES? To prevent the DB record growing forever.
    """
    trimmed = history[-MAX_MESSAGES:]
    AgentSession.objects.update_or_create(
        session_id=session_id,
        defaults={
            "user_id": user.id if user else None,
            "history": json.dumps(trimmed)
        }
    )


def clear_session(session_id: str, user=None) -> None:
    """
    Delete session from DB — called on logout or manual reset.
    """
    AgentSession.objects.filter(session_id=session_id).delete()