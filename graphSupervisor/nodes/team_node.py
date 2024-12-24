import os
from langgraph.types import *
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.constants import END

from graphSupervisor.states import ResearchState



llm = ChatOpenAI(model_name=os.getenv("MODEL"))


def analyst_node(state: ResearchState):
    prompt = state["analyst_prompt"]
    return {"messages": ["Hello world"]}


def reviewer_node(state: ResearchState):
    prompt = state["reviewer_prompt"]
    print(len(state.get("messages", [])))
    return {"messages": ["Hello world"]}


# def sender_node(state: ResearchOutputState):
#     return {"reviewer_final_overview": state["messages"][-1]}



# def should_continue(state: ResearchState):
#     # Check if the number of messages is 6 or more
#     if len(state.get("messages", [])) >= 6:
#         # Return the END constant and the overall state update
#         return END
#
#     # If the condition is not met, return the next node
#     return "Analyst"


def should_continue(state: ResearchState) -> str | Command[Literal[END]]:
    # Check if the number of messages is 6 or more
    if len(state.get("messages", [])) >= 6:
        # Return the END constant and the overall state update
        state["reviews"].append(state["messages"][-1])
        return END

    # If the condition is not met, return the next node
    return "Analyst"

