from typing import Any, Dict
from uuid import uuid4


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def start(self) -> str:
        sid = str(uuid4())
        self._sessions[sid] = {}
        return sid

    def end(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self._sessions.setdefault(session_id, {})
