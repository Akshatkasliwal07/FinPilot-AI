from typing import Any, Protocol


class ConversationMemoryStore(Protocol):
    """
    Interface that both in-memory and database-backed stores must implement.
    """

    def add_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        ...

    def build_context(
        self,
        session_id: str,
        limit: int = 6,
    ) -> str:
        ...

    def clear(self, session_id: str) -> None:
        ...