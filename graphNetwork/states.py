import operator
from typing import List, Annotated, Sequence, TypedDict, Union, Dict
from langgraph.graph import MessagesState
from langchain_core.agents import AgentAction, AgentFinish

from graphNetwork.schemas import Agent


class OverallState(MessagesState):
    topic: str
    questionnaire: str
    reviews: Annotated[List[str], operator.add]  # Four reviewers answers


class AgentState(MessagesState):
    code_name: str
    name: str
    description: str
    agent_topic: str
    agent_questionnaire: str
    # Local analysts messages
    current_analysis: str
    questions_asked: int
    questions_from_agents: Annotated[list[Dict[str, str]], operator.add]
    answers_from_agents: Annotated[list[Dict[str, str]], operator.add]

    messages: Annotated[List[str], operator.add]
    input: Dict[str, str]

    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
