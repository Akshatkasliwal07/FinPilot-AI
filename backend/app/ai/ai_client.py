from app.ai.ai_schema import (
    AIAnalysisRequest,
    AIAnalysisResponse
)


class AIClient:

    @staticmethod
    def analyze(
        request: AIAnalysisRequest
    ) -> AIAnalysisResponse:
        """
        Placeholder for the AI team.

        They will replace this implementation with
        their model or API call.
        """

        return AIAnalysisResponse(
            recommendation="HOLD",
            confidence=0,
            reason="AI service not connected."
        )
    from app.ai.ai_schema import (
    AIAnalysisRequest,
    AIAnalysisResponse,
)
from ai.services.backend_analysis_service import (
    run_backend_analysis,
)


class AIClient:

    @staticmethod
    def analyze(
        request: AIAnalysisRequest,
    ) -> AIAnalysisResponse:

        result = run_backend_analysis(
            symbol=request.symbol,
            current_price=request.current_price,
            technical_indicators=request.technical_indicators,
            latest_news=request.latest_news,
        )

        if not result["success"]:
            raise RuntimeError(result["message"])

        return AIAnalysisResponse(
            recommendation=result["data"]["recommendation"],
            confidence=result["data"]["confidence"],
            reason=result["data"]["reason"],
        )