import operator
from typing import List, Annotated, Sequence, TypedDict, Union

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from langchain_core.agents import AgentAction, AgentFinish

# Overall state f
class OverallState(TypedDict):
    topic: str
    messages: Annotated[Sequence[BaseMessage], operator.add]


class AgentState(TypedDict):
    """
    The state of the agent.
    """
    agent_name: str
    agent_descripion: str
    input: str
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
