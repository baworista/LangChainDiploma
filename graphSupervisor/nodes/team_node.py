import os
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import END

from graphSupervisor.states import ResearchState

llm = ChatOpenAI(model_name=os.getenv("MODEL"))

# team_prompt"""
# You are in the analyst->reviewer team.
# Based on your role you should
# """

def analyst_node(state):
    print("Analyst node activated.")

    if len(state.get("messages", [])) < 1:
        team_questionnaire = state["team_questionnaire"]
        state["messages"].append(HumanMessage(f"Your questionnaire is: {team_questionnaire}"))

    sys_msg = SystemMessage(state["analyst_prompt"])
    return {"messages": [llm.invoke([sys_msg] + state["messages"])]}
    # return {"messages": [AIMessage("Analyst answer " + state["analyst_prompt"][0:25])]  + state.get("messages", [])} # For test


def reviewer_node(state):
    print("Reviewer node activated.")
    sys_msg = SystemMessage(state["reviewer_prompt"])
    return {"messages": [llm.invoke([sys_msg] + state["messages"])]}
    # return {"messages": [AIMessage("Reviewers answer " + state["reviewer_prompt"][0:25])] + state.get("messages", [])} # For test


def should_continue(state: ResearchState):
    messages = state.get("messages", [])
    # Check if the number of messages is 6 or more
    if len(messages) >= 6:

        # Return the END constant and the overall state update
        state["reviews"].append(messages[-1].content)
        return END

    # If the condition is not met, return the next node
    return "Analyst"

