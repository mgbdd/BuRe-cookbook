from typing import List, Annotated, TypedDict, Dict, Any
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_query : str
    generated_recipe : Dict[str, Any] | None
    searched_recipe : Dict[str, Any] | None
    tool : str | None