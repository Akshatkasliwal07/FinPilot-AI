from ai.agents.news_agent import news_agent
from ai.agents.company_research_agent import company_research_agent
from ai.agents.technical_agent import technical_agent
from ai.agents.portfolio_agent import portfolio_agent
from ai.agents.risk_agent import risk_agent
from ai.agents.report_agent import report_agent


def news_node(state):
    print("NEWS NODE")

    result = news_agent(
        state["company"]
    )

    state["news_data"] = result

    return state



def research_node(state):
    print("RESEARCH NODE")

    result = company_research_agent(
        state["company"]
    )

    state["research_data"] = result

    return state



def technical_node(state):
    print("TECHNICAL NODE")

    result = technical_agent(
        state["symbol"]
    )

    state["technical_data"] = result

    return state



def portfolio_node(state):
    print("PORTFOLIO NODE")

    result = portfolio_agent(
        state
    )

    state["portfolio_data"] = result

    return state


def risk_node(state):

    print("RISK NODE")

    result = risk_agent(
        state
    )

    state["risk_analysis"] = result

    return state


def report_node(state):

    print("REPORT NODE")

    result = report_agent(
        state
    )

    state["final_report"] = result

    return state