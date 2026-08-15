from newsapi import NewsApiClient

from ai.config.settings import NEWS_API_KEY


newsapi = NewsApiClient(api_key=NEWS_API_KEY)


FINANCIAL_KEYWORDS = (
    "earnings",
    "revenue",
    "profit",
    "loss",
    "stock",
    "share",
    "market",
    "investor",
    "investment",
    "financial",
    "valuation",
    "guidance",
    "sales",
    "lease",
    "leasing",
    "business",
)

def fetch_company_news(company: str) -> list[dict]:
    if not company or not company.strip():
        return []

    company_name = company.strip()
    company_lower = company_name.lower()

    response = newsapi.get_everything(
        q=f'"{company_name}"',
        language="en",
        sort_by="publishedAt",
        page_size=30,
    )

    relevant_articles = []

    for article in response.get("articles", []):
        title = article.get("title", "")
        description = article.get("description", "")
        text = f"{title} {description}".lower()

        mentions_company = company_lower in text
        has_financial_context = any(
            keyword in text
            for keyword in FINANCIAL_KEYWORDS
        )

        if mentions_company and has_financial_context:
            relevant_articles.append(article)

    return relevant_articles[:5]