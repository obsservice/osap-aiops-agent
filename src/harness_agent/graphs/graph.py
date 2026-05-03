from langgraph.graph import StateGraph, START, END

from harness_agent.graphs.nodes.normalize import normalize_request
from harness_agent.graphs.nodes.response import compose_response
from harness_agent.graphs.state import AgentState


def make_lead_graph():
    builder = StateGraph(AgentState)

    builder.add_node("normalize_request", normalize_request)
    builder.add_node("compose_response", compose_response)

    builder.add_edge(START, "normalize_request")
    builder.add_edge("normalize_request", "compose_response")
    builder.add_edge("compose_response", END)

    return builder.compile()
