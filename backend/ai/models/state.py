from typing import Any, TypedDict


class FinPilotState(TypedDict, total=False):
    user_query: str

    company: str | None
    symbol: str | None
    plan: str

    market_data: dict[str, Any]
    news_data: dict[str, Any]
    company_data: dict[str, Any]

    fundamental_analysis: dict[str, Any]
    technical_analysis: dict[str, Any]
    portfolio_analysis: dict[str, Any]
    risk_analysis: dict[str, Any]

    final_report: dict[str, Any]