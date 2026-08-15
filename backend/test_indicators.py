from app.api.alpha_vantage import AlphaVantageAPI
from app.ai.technical_analysis import TechnicalAnalysis

history = AlphaVantageAPI.get_daily_history("IBM")

indicators = TechnicalAnalysis.calculate(history)

print(indicators)