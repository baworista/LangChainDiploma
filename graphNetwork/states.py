import operator
from typing import List, Annotated, Sequence, TypedDict, Union, Dict
from langgraph.graph import MessagesState
from langchain_core.agents import AgentAction, AgentFinish
from langgraph.prebuilt.chat_agent_executor import AgentState

from graphNetwork.schemas import Agent


class OverallState(MessagesState):
    topic: str
    questionnaire: str
    reviews: Annotated[List[str], operator.add]  # Four reviewers answers


class CustomAgentState(AgentState):
    code_name: str
    name: str
    description: str
    agent_topic: str
    agent_questionnaire: str
    # Local analysts messages
    current_analysis: str
    questions_asked: int
    reviews: Annotated[List[str], operator.add]  # Four reviewers answers
    questions_from_agents: Annotated[list[Dict[str, str]], operator.add]
    answers_from_agents: Annotated[list[Dict[str, str]], operator.add]
