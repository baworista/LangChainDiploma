from langgraph.constants import END

from supervisor_simple.states import ResearchState


def analyst_node(state: ResearchState):
    prompt = state["analyst_prompt"]
    pass


def reviewer_node(state: ResearchState):
    prompt = state["reviewer_prompt"]
    pass


def should_continue(state: ResearchState):
    max_iterations = state["max_iterations"]
    current_iteration = state["current_iteration"]

    if current_iteration >= max_iterations:
        return END

    return "Analyst"
