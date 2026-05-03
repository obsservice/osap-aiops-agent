import structlog

from harness_agent.graphs.state import AgentState

log = structlog.get_logger(__name__)


def normalize_request(state: AgentState) -> AgentState:
    log.info("normalize request", state=state)
    return {
        **state,
    }
