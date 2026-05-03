from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    request_id: str
    session_id: str
    user_query: str
    results: str
