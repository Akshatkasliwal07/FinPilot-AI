from pydantic import BaseModel, Field


class AIAnalysisRequest(BaseModel):
    symbol: str
    current_price: float
    technical_indicators: dict = Field(
        default_factory=dict
    )
    latest_news: list = Field(
        default_factory=list
    )


class AIAnalysisResponse(BaseModel):
    recommendation: str
    confidence: int
    reason: str


class AIDecisionResponse(BaseModel):
    symbol: str
    recommendation: str
    confidence: int
    reason: str
    current_price: float | None = None
    market_status: str = "unknown"
    technical_score: int = 0
    news_sentiment: str = "Neutral"
    risk_level: str = "Moderate"