from ai.config.llm import llm
from ai.memory import (
    ConversationMemoryStore,
    conversation_memory,
)
from ai.models.response import error_response, success_response
from ai.prompts.chat_prompt import FINPILOT_CHAT_PROMPT


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    return str(content)


def chat_with_finpilot(
    session_id: str,
    user_query: str,
    memory_store: ConversationMemoryStore | None = None,
) -> dict:
    """
    Generate a FinPilot AI chat response with recent conversation context.
    """
    if not session_id or not session_id.strip():
        return error_response("session_id is required.")

    if not user_query or not user_query.strip():
        return error_response("user_query is required.")

    try:
        memory_context = conversation_memory.build_context(
            session_id=session_id,
            limit=6,
        )

        prompt = FINPILOT_CHAT_PROMPT.format(
            memory_context=memory_context,
            user_query=user_query.strip(),
        )

        response = llm.invoke(prompt)
        answer = _extract_text(response.content)

        conversation_memory.add_turn(
            session_id=session_id,
            user_message=user_query,
            assistant_message=answer,
        )

        return success_response(
            "Chat response generated successfully.",
            {
                "session_id": session_id,
                "answer": answer,
            },
        )

    except Exception as error:
        return error_response(str(error))