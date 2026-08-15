from ai.tools.yahoo_tool import get_stock_data
from ai.models.response import success_response


def market_agent(state):
    """
    Fetch latest stock market data from Yahoo Finance.
    """

    try:
        symbol = state.get("symbol")

        if not symbol:
            raise Exception("Stock symbol not found.")

        stock_data = get_stock_data(symbol)

        return success_response(
            "Market data fetched successfully.",
            stock_data
        )

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }