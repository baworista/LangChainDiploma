import os
from langgraph.types import *
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.constants import END

from graphSupervisor.states import ResearchState

llm = ChatOpenAI(model_name=os.getenv("MODEL"))


def analyst_node(state: ResearchState):
    prompt = state["analyst_prompt"]
    descr = state["analyst_prompt"][0:30]
    return {"messages": ["Hello world Assystent: " + descr]}


def reviewer_node(state: ResearchState):
    prompt = state["reviewer_prompt"]
    descr = state["reviewer_prompt"][0:30]
    print(len(state.get("messages", [])))
    return {"messages": ["Hello world Reviewer: " + descr]}



def should_continue(state: ResearchState):
    # Check if the number of messages is 6 or more
    if len(state.get("messages", [])) >= 6:
        # Return the END constant and the overall state update
        state["reviews"].append(state["messages"][-1])
        return END

    # If the condition is not met, return the next node
    return "Analyst"

