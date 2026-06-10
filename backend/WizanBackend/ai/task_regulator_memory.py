# In-memory session store (use Redis in production)
_sessions = {}

def get_session(session_id):
    return _sessions.get(session_id, [])

def save_session(session_id, memory):
    _sessions[session_id] = memory

def clear_session(session_id):
    _sessions.pop(session_id, None)