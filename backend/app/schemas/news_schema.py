from pydantic import BaseModel


class NewsArticle(BaseModel):
    title: str
    source: str
    published_at: str
    url: str
    sentiment: str


class NewsResponse(BaseModel):
    symbol: str
    overall_sentiment: str
    confidence: int
    articles: list[NewsArticle]