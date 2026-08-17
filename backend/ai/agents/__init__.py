def __getattr__(name):
    if name == "answer_pdf_question":
        from ai.agents.pdf_rag_agent import answer_pdf_question
        return answer_pdf_question
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")