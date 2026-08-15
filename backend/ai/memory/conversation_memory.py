from collections import deque
from threading import RLock
from typing import Any


class ConversationMemory:
    """
    Thread-safe in-process conversation memory.

    Use this during development. Replace or extend it with a database-backed
    repository when the backend/database contract is available.
    """

    def __init__(self, max_turns: int = 10):
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1.")

        self.max_turns = max_turns
        self._sessions: dict[str, deque[dict[str, Any]]] = {}
        self._lock = RLock()

    def add_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not session_id.strip():
            raise ValueError("session_id is required.")

        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = deque(
                    maxlen=self.max_turns
                )

            self._sessions[session_id].append(
                {
                    "user_message": user_message.strip(),
                    "assistant_message": assistant_message.strip(),
                    "metadata": metadata or {},
                }
            )

    def get_turns(
        self,
        session_id: str,
        limit: int = 6,
    ) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be at least 1.")

        with self._lock:
            turns = list(self._sessions.get(session_id, []))

        return turns[-limit:]

    def build_context(
        self,
        session_id: str,
        limit: int = 6,
    ) -> str:
        turns = self.get_turns(session_id, limit)

        if not turns:
            return "No prior conversation history."

        context_parts = []

        for turn in turns:
            context_parts.append(
                f"""
User: {turn["user_message"]}
Assistant: {turn["assistant_message"]}
""".strip()
            )

        return "\n\n".join(context_parts)

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


conversation_memory = ConversationMemory()