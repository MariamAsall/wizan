from tasks.models import AgentMemory
from ai.llm import safe_llm_call   # ← THE fix — use our safe function

def save_session_summary(user_id, session_id, conversation_history):
    """
    Called at the END of every session.
    Why? So next session the agent remembers what happened before.
    """
    # Build a readable transcript from the conversation history
    transcript = ""
    for turn in conversation_history:
        role = turn["role"]
        for part in turn["parts"]:
            if isinstance(part, dict) and "text" in part:
                transcript += f"{role}: {part['text']}\n"

    if not transcript.strip():
        return  

    prompt = f"""
Summarize this conversation in 2-3 lines maximum.
Focus on: what tasks were allowed, what was postponed, and how the user felt.
Be factual and brief.

Conversation:
{transcript}
"""
    # Simply call your safe function
    summary_text = safe_llm_call(prompt)

    AgentMemory.objects.create(
        user_id=user_id,
        session_id=session_id,
        summary=summary_text
    )


def load_past_summaries(user_id, count=3):
    """
    Called at the START of every session.
    Why 3? Enough context without overloading the prompt.
    """
    records = AgentMemory.objects.filter(
        user_id=user_id
    ).order_by('-created_at')[:count]

    if not records:
        return ""  # first time user — no history yet

    lines = []
    for i, record in enumerate(reversed(records), 1):
        lines.append(f"Session {i} ({record.created_at.date()}): {record.summary}")

    return "\n".join(lines)