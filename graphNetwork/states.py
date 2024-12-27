import operator
from typing import List, Annotated, Sequence, TypedDict, Union, Dict

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from langchain_core.agents import AgentAction, AgentFinish

from graphNetwork.schemas import Agent


# Overall state f
class OverallState(MessagesState):
    topic: str
    questionnaire: str
    agents: list[Agent]


class AgentState(MessagesState):
    name: str
    description: str
    topic: str
    current_analysis: str
    # Local analysts messages
    questions_asked: int

    input: Dict[str, str]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


# class AgentState(MessagesState):
#     """
#     The state of the agent.
#     """
#     agent_name: str
#     agent_descripion: str
