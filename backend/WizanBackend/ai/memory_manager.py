"""
memory_manager.py  –  DB-backed session memory using AgentMemory model.
Replaces the in-memory dict so sessions survive server restarts.
Stored format inside memory_data:
    { "messages": [ {"role": "user"|"model", "content": "..."}, ... ] }
"""

from tasks.models import AgentMemory

MAX_MESSAGES = 10  # how many messages to load on agent startup


# ── read ──────────────────────────────────────────────────────────────────────

def get_session(session_id: str, user=None) -> list[dict]:
    """
    Return the last MAX_MESSAGES messages for this session.
    If user is provided it is used to scope the lookup (recommended).
    Returns an empty list when no history exists.
    """
    qs = AgentMemory.objects.filter(session_id=session_id)
    if user is not None:
        qs = qs.filter(user=user)

    record = qs.first()
    if record is None:
        return []

    messages = record.memory_data.get("messages", [])
    return messages[-MAX_MESSAGES:]          # load only the last N messages


# ── write ─────────────────────────────────────────────────────────────────────

def save_session(session_id: str, messages: list[dict], user=None) -> None:
    """
    Persist the full message list for this session.
    Creates a new record or updates the existing one (upsert).
    user is required to create a new record; ignored on update when not provided.
    """
    qs = AgentMemory.objects.filter(session_id=session_id)
    if user is not None:
        qs = qs.filter(user=user)

    record = qs.first()

    if record is not None:
        record.memory_data = {"messages": messages}
        record.save(update_fields=["memory_data", "updated_at"])
    else:
        if user is None:
            raise ValueError(
                "user is required when creating a new AgentMemory record"
            )
        AgentMemory.objects.create(
            session_id=session_id,
            user=user,
            memory_data={"messages": messages},
        )


# ── delete ────────────────────────────────────────────────────────────────────

def clear_session(session_id: str, user=None) -> None:
    """Delete the session record entirely."""
    qs = AgentMemory.objects.filter(session_id=session_id)
    if user is not None:
        qs = qs.filter(user=user)
    qs.delete()
