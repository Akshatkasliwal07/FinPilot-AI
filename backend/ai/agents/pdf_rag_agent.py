from ai.config.gemini import llm
from ai.models.response import error_response, success_response
from ai.prompts.pdf_rag_prompt import PDF_RAG_PROMPT
from ai.vectorstore import search_documents


def _extract_text(content) -> str:
    """
    Safely convert Gemini response content into text.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    return str(content)


def answer_pdf_question(
    question: str,
    source: str,
    limit: int = 4,
) -> dict:
    """
    Answer one question using chunks from one indexed PDF only.
    """
    if not question or not question.strip():
        return error_response("Question must be a non-empty string.")

    if not source or not source.strip():
        return error_response("PDF source filename is required.")

    try:
        results = search_documents(
            query=question,
            limit=limit,
            where={"source": source},
        )

        if not results:
            return error_response(
                "No relevant content was found in the selected PDF."
            )

        context_sections = []

        for result in results:
            metadata = result.get("metadata", {})

            context_sections.append(
                f"""
[Source: {metadata.get("source", source)}
Page: {metadata.get("page", "Unknown")}]

{result.get("document", "")}
"""
            )

        context = "\n---\n".join(context_sections)

        prompt = PDF_RAG_PROMPT.format(
            context=context,
            question=question.strip(),
        )

        response = llm.invoke(prompt)
        answer = _extract_text(response.content)

        citations = [
            {
                "source": item["metadata"].get("source", source),
                "page": item["metadata"].get("page"),
                "chunk_index": item["metadata"].get("chunk_index"),
            }
            for item in results
        ]

        return success_response(
            "PDF question answered successfully.",
            {
                "answer": answer,
                "source": source,
                "citations": citations,
                "chunks_retrieved": len(results),
            },
        )

    except Exception as error:
        return error_response(str(error))