from app.ai.ai_client import AIClient
from app.ai.ai_schema import (
    AIAnalysisRequest,
    AIAnalysisResponse,
)


ai_client = AIClient()


def analyze_stock(
    request: AIAnalysisRequest,
) -> AIAnalysisResponse:
    return ai_client.analyze(request)