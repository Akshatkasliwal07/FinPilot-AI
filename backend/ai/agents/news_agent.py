from ai.tools.news_tool import fetch_company_news
from ai.prompts.news_prompt import NEWS_SUMMARY_PROMPT
from ai.config.gemini import llm


def news_agent(company: str):

    try:

        print("NEWS AGENT START")

        articles = fetch_company_news(company)


        if not articles:
            return {
                "success": False,
                "message": "No news found",
                "data": {
                    "summary": "",
                    "articles": []
                }
            }


        news_text = ""

        for article in articles[:5]:

            title = article.get("title", "")
            description = article.get("description", "")

            news_text += f"""
Title:
{title}

Description:
{description}

"""


        prompt = NEWS_SUMMARY_PROMPT.format(
            news=news_text
        )


        response = llm.invoke(prompt)


        summary = response.content


        # Gemini sometimes returns list
        if isinstance(summary, list):

            summary = "".join(
                item.get("text","")
                for item in summary
                if isinstance(item,dict)
            )


        return {

            "success": True,

            "message":
            "News summarized successfully",

            "data": {

                "summary": summary,

                "articles": articles

            }

        }


    except Exception as e:


        return {

            "success": False,

            "message": str(e),

            "data": {}

        }