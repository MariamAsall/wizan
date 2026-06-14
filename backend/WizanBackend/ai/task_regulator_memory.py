# """
# task_regulator_memory.py  –  Session memory for the Task Regulator agent.
# Previously used an in-memory dict; now backed by AgentMemory via memory_manager
# so history survives server restarts and is available on agent startup.
# """

# from ai.memory_manager import get_session, save_session, clear_session  # noqa: re-export


# # The three functions below keep the same public interface as before
# # so task_regulator_agent.py needs zero changes.

# def get_regulator_session(session_id: str, user=None) -> list[dict]:
#     """
#     Load past messages for this session from the DB.
#     Called on agent startup so the agent has conversational context.
#     Returns at most the last 10 messages (controlled by memory_manager.MAX_MESSAGES).
#     """
#     return get_session(session_id, user=user)


# def save_regulator_session(session_id: str, messages: list[dict], user=None) -> None:
#     """Persist updated message history after each agent turn."""
#     save_session(session_id, messages, user=user)


# def clear_regulator_session(session_id: str, user=None) -> None:
#     """Clear session (e.g. on logout or manual reset)."""
#     clear_session(session_id, user=user)


# In-memory session store (use Redis in production)
f# ai/task_regulator_memory.py

from ai.memory_manager import (
    get_session  as _db_get_session,
    save_session as _db_save_session,
    clear_session as _db_clear_session,
)

# Why aliases with underscore?
# To avoid the function name colliding with what we define below.

def get_session(session_id: str, user=None) -> list:
    return _db_get_session(session_id, user=user)

def save_session(session_id: str, messages: list, user=None) -> None:
    _db_save_session(session_id, messages, user=user)

def clear_session(session_id: str, user=None) -> None:
    _db_clear_session(session_id, user=user)