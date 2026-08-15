from app.api.alpha_vantage import AlphaVantageAPI

history = AlphaVantageAPI.get_daily_history("IBM")

print(len(history))