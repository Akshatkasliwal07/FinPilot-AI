from typing import TypedDict
from langgraph.graph import StateGraph, END
from ai.agents.planner_agent import planner_agent
from ai.agents.portfolio_agent import portfolio_agent

# Shared state between agents
class AgentState(TypedDict):
    user_query: str
    plan: str


# Planner Node
def planner_node(state: AgentState):
    plan = planner_agent(state["user_query"])

    return {
        "plan": plan
    }


# Create graph
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", END)

graph = workflow.compile()