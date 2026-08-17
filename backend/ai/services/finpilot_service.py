from pathlib import Path

from ai.chains import chat_with_finpilot
from ai.langgraph.workflow import graph
from ai.models.response import error_response, success_response


def run_stock_research(user_query: str) -> dict:
    """
    Run the complete LangGraph equity-research workflow.
    """
    if not user_query or not user_query.strip():
        return error_response("user_query is required.")

    try:
        result = graph.invoke(
            {
                "user_query": user_query.strip(),
            }
        )

        final_report = result.get("final_report")

        if not final_report:
            return error_response(
                "Research workflow completed without a final report."
            )

        return success_response(
            "Research completed successfully.",
            {
                "report": final_report,
                "workflow_data": result,
            },
        )

    except Exception as error:
        return error_response(str(error))


def run_chat(
    session_id: str,
    user_query: str,
) -> dict:
    """
    Run memory-aware FinPilot AI chat.
    """
    return chat_with_finpilot(
        session_id=session_id,
        user_query=user_query,
    )


def index_uploaded_pdf(
    server_file_path: str | Path,
) -> dict:
    """
    Index a PDF already stored by the FastAPI backend.

    Never accept a raw filesystem path directly from the frontend.
    """
    try:
        from ai.rag import index_pdf
        return index_pdf(server_file_path)
    except Exception as error:
        return error_response(str(error))


def ask_uploaded_pdf(
    question: str,
    source: str,
) -> dict:
    """
    Answer a question using only one indexed PDF.
    """
    from ai.agents.pdf_rag_agent import answer_pdf_question
    return answer_pdf_question(
        question=question,
        source=source,
    )

