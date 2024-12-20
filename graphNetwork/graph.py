import operator
from typing import Literal, Annotated, List

from langchain.chains.question_answering.map_reduce_prompt import messages
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import StateGraph, START
from langgraph.types import Command
from sqlalchemy import Sequence

from graphNetwork.prompts import agent_prompt
from graphNetwork.schemas import Agent
from supervisor_simple.states import OverallState

model = ChatOpenAI()


class State(OverallState):
    topic: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    agents: List[Agent]


def agent_1(state: State) -> Command[Literal["agent_2", "agent_3", "agent_4", END]]:
    agent = state.agents[0]
    prompt = agent_prompt + messages
    response = model.invoke(prompt)
    # route to one of the agents or exit based on the LLM's decision
    # if the LLM returns "__end__", the graph will finish execution
    return Command(
        goto=response["next_agent"],
        update={"messages": [response["content"]]},
    )


def agent_2(state: State) -> Command[Literal["agent_1", "agent_3", "agent_4", END]]:
    agent = state.agents[1]
    response = model.invoke(...)
    return Command(
        goto=response["next_agent"],
        update={"messages": [response["content"]]},
    )


def agent_3(state: State) -> Command[Literal["agent_1", "agent_2", "agent_4", END]]:
    agent = state.agents[2]
    response = model.invoke(...)
    return Command(
        goto=response["next_agent"],
        update={"messages": [response["content"]]},
    )


def agent_4(state: OverallState) -> Command[Literal["agent_1", "agent_2", "agent_3", END]]:
    agent = state.agents[2]
    response = model.invoke(...)

    return Command(
        goto=response["next_agent"],
        update={"messages": [response["content"]]},
    )


builder = StateGraph(State)
builder.add_node(agent_1)
builder.add_node(agent_2)
builder.add_node(agent_3)
builder.add_node(agent_4)

builder.add_edge(START, "agent_1")

network = builder.compile()
