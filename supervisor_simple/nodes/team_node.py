import os

from langchain_openai import ChatOpenAI

from supervisor_simple.states import ResearchState, OverallState

from langgraph.constants import END

llm = ChatOpenAI(model_name=os.getenv("MODEL"))


def analyst_node(state: ResearchState):
    prompt = state["analyst_prompt"]
    return {"messages": ["Hello world"]}


def reviewer_node(state: ResearchState):
    prompt = state["reviewer_prompt"]
    print(len(state.get("messages", [])))
    return {"messages": ["Hello world"]}


def should_continue(state: ResearchState):
    # Check if the number of messages is 6 or more
    if len(state.get("messages", [])) >= 6:
        # Return the END constant and the overall state update
        return END

    # If the condition is not met, return the next node
    return "Analyst"

