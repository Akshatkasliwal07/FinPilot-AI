from langgraph.graph import END, StateGraph

from ai.agents.company_research_agent import company_research_agent
from ai.agents.fundamental_agent import fundamental_agent
from ai.agents.market_agent import market_agent
from ai.agents.news_agent import news_agent
from ai.agents.planner_agent import planner_agent
from ai.agents.portfolio_agent import portfolio_agent
from ai.agents.report_agent import report_agent
from ai.agents.risk_agent import risk_agent
from ai.agents.technical_agent import technical_agent
from ai.models.response import error_response
from ai.models.state import FinPilotState


def planner_node(state: FinPilotState) -> FinPilotState:
    try:
        state["plan"] = planner_agent(state.get("user_query", ""))
    except Exception as error:
        state["plan"] = "Fallback research plan"
        print(f"Planner error: {error}")

    return state


def symbol_node(state: FinPilotState) -> FinPilotState:
    query = state.get("user_query", "").lower()

    symbols = {
        "tata motors": "TMCV.NS",
        "reliance": "RELIANCE.NS",
        "infosys": "INFY.NS",
        "hdfc bank": "HDFCBANK.NS",
        "tcs": "TCS.NS",
        "sbi": "SBIN.NS",
    }

    for company, symbol in symbols.items():
        if company in query:
            state["company"] = company
            state["symbol"] = symbol
            return state

    state["company"] = None
    state["symbol"] = None
    return state


def market_node(state: FinPilotState) -> FinPilotState:
    try:
        # market_agent returns a JSON response.
        state["market_data"] = market_agent(state)
    except Exception as error:
        state["market_data"] = error_response(str(error))

    return state


def news_node(state: FinPilotState) -> FinPilotState:
    try:
        company = state.get("company")

        if not company:
            raise ValueError("Company could not be resolved from the request.")

        state["news_data"] = news_agent(company)
    except Exception as error:
        state["news_data"] = error_response(str(error))

    return state


def company_node(state: FinPilotState) -> FinPilotState:
    try:
        symbol = state.get("symbol")

        if not symbol:
            raise ValueError("Stock symbol could not be resolved.")

        state["company_data"] = company_research_agent(symbol)
    except Exception as error:
        state["company_data"] = error_response(str(error))

    return state


def fundamental_node(state: FinPilotState) -> FinPilotState:
    try:
        symbol = state.get("symbol")

        if not symbol:
            raise ValueError("Stock symbol could not be resolved.")

        state["fundamental_analysis"] = fundamental_agent(symbol)
    except Exception as error:
        state["fundamental_analysis"] = error_response(str(error))

    return state


def technical_node(state: FinPilotState) -> FinPilotState:
    try:
        symbol = state.get("symbol")

        if not symbol:
            raise ValueError("Stock symbol could not be resolved.")

        state["technical_analysis"] = technical_agent(symbol)
    except Exception as error:
        state["technical_analysis"] = error_response(str(error))

    return state


def portfolio_node(state: FinPilotState) -> FinPilotState:
    state["portfolio_analysis"] = portfolio_agent(state)
    return state


def risk_node(state: FinPilotState) -> FinPilotState:
    state["risk_analysis"] = risk_agent(state)
    return state


def report_node(state: FinPilotState) -> FinPilotState:
    state["final_report"] = report_agent(state)
    return state


workflow = StateGraph(FinPilotState)

workflow.add_node("planner", planner_node)
workflow.add_node("symbol", symbol_node)
workflow.add_node("market", market_node)
workflow.add_node("news", news_node)
workflow.add_node("company", company_node)
workflow.add_node("fundamental", fundamental_node)
workflow.add_node("technical", technical_node)
workflow.add_node("portfolio", portfolio_node)
workflow.add_node("risk", risk_node)
workflow.add_node("report", report_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", "symbol")
workflow.add_edge("symbol", "market")
workflow.add_edge("market", "news")
workflow.add_edge("news", "company")
workflow.add_edge("company", "fundamental")
workflow.add_edge("fundamental", "technical")
workflow.add_edge("technical", "portfolio")
workflow.add_edge("portfolio", "risk")
workflow.add_edge("risk", "report")
workflow.add_edge("report", END)

graph = workflow.compile()