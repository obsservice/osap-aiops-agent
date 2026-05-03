import structlog

from harness_agent.graphs.state import AgentState

log = structlog.get_logger(__name__)


def compose_response(state: AgentState) -> AgentState:
    results = "todo ..."
    log.info("compose response")
    return {
        **state,
        "results": results,
    }
