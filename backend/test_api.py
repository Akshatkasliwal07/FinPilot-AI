from app.api.alpha_vantage import AlphaVantageAPI

quote = AlphaVantageAPI.get_stock_quote("IBM")

print(quote)