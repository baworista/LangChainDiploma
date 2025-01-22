"""
Module for managing the interaction between analysts and reviewers in a supervisor workflow.

This module defines nodes for the `Analyst` and `Reviewer` roles in a research team, facilitating
a structured exchange of analyses and feedback. It also provides a mechanism to determine the
next workflow step based on the state of the conversation.

Functions:
    - analyst_node: Handles the needs analysis performed by the analyst.
    - reviewer_node: Handles the feedback and review provided by the reviewer.
    - should_continue: Determines whether to proceed to the next step or end the workflow.

Constants:
    - analyst_prompt: Template for the analyst's role, context, and guidelines.
    - reviewer_prompt: Template for the reviewer's role, context, and guidelines.
"""
import os
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import END

from graphSupervisor.states import ResearchState

llm = ChatOpenAI(model_name=os.getenv("MODEL"))

analyst_prompt = """
# Role & Context
You are: {person}
You are in {team} with {reviewer}, who will provide a review and share their opinion with you.
You are tasked with performing a **needs analysis** for your customer on the topic: {topic}

# Data Source
Here are the **questionnaire results**: {questionnaire}

# Objective
Your primary goal is to **analyze the current state of the customer** based on the questionnaire results and, once received, **integrate the reviewer's feedback** into your analysis.

# Guidelines
- Generate **only an analysis** based on the questionnaire results.
- Focus **solely on your persona, competencies, and tasks**.

# Constraints
- **Do not analyze aspects outside of your persona or competencies.**
- **Do not recommend any solutions yet.**

# Final Note
Keep your analysis focused, clear, and aligned with the given responsibilities and data.
Behave like a provided persona.
Start your messages from your name!
"""


reviewer_prompt = """
# Role & Context
You are: {person}
You are in {team} with {analyst}, who will make an analysis and share it with you.
You are tasked with assisting your analyst on the topic: {topic}

# Data Source
Here are the questionnaire results: {questionnaire}

# Objective
Your primary task is to create a constructive and insightful review based on the provided analysis and questionnaire results.

# Guidelines
1. **Constructive:** Provide actionable and helpful recommendations.
2. **Specific:** Avoid generalities; include clear examples directly tied to the analysis.
3. **Manageable:** Ensure your recommendations are practical and achievable for the customer.

# Constraints
- Base your recommendations **solely on the provided analysis**.
- Stay **aligned with your role, expertise, and responsibilities**.
- Avoid commenting on aspects outside your defined scope.

# Final Note
Focus on delivering a review that adds value, clarity, and direction to the analysis provided.
Behave like a provided persona.
Start your messages from your name!
"""


def analyst_node(state):
    """
    Handles the needs analysis performed by the analyst.

    This function generates a structured analysis based on the provided questionnaire results and
    optionally integrates feedback from the reviewer if available.

    Args:
        state (ResearchState): The current state of the research team containing:
            - "team_topic" (str): The topic assigned to the team.
            - "name" (str): The name of the team.
            - "description" (str): A description of the team's responsibilities.
            - "reviewer" (Person): Information about the reviewer.
            - "analyst" (Person): Information about the analyst.
            - "team_questionnaire" (str): The questionnaire results.
            - "messages" (list): Previous messages exchanged in the workflow.

    Returns:
        dict: Updated state with the analyst's analysis added to the "messages".
    """
    topic = state["team_topic"]

    team_name = state["name"]
    team_description = state["description"]

    reviewer_info = state["reviewer"]
    analyst_info = state["analyst"]

    questionnaire = state["team_questionnaire"]

    analyst_name = state["analyst"].name
    print(f"Analyst {analyst_name} from {team_name} activated.")

    system_prompt = analyst_prompt.format(topic=topic,
                                          team = team_name + "\n" + team_description,
                                          reviewer = reviewer_info,
                                          person = analyst_info,
                                          questionnaire = questionnaire)

    messages = state["messages"]

    if len(messages) != 0:
        last_message = "Your previous report: \n" + messages[-2].content + "\n\n\nReviewers recommendations: \n" + messages[-1].content
    else:
        last_message = "This is the beginning of conversation. Make your initial analysis based on the questionnaire results."

    llm_messages = [SystemMessage(content=system_prompt),
                last_message
                ]

    return {"messages": [llm.invoke(llm_messages).content]}
    # return {"messages": [AIMessage("Analyst answer " + state["analyst_prompt"][0:25])]  + state.get("messages", [])} # For test


def reviewer_node(state):
    """
    Handles the feedback and review provided by the reviewer.

    This function generates constructive feedback based on the analyst's analysis and the provided
    questionnaire results.

    Args:
        state (ResearchState): The current state of the research team containing:
            - "team_topic" (str): The topic assigned to the team.
            - "name" (str): The name of the team.
            - "description" (str): A description of the team's responsibilities.
            - "reviewer" (Person): Information about the reviewer.
            - "analyst" (Person): Information about the analyst.
            - "team_questionnaire" (str): The questionnaire results.
            - "messages" (list): Previous messages exchanged in the workflow.

    Returns:
        dict: Updated state with the reviewer's feedback added to the "messages".
    """
    topic = state["team_topic"]

    team_name = state["name"]
    team_description = state["description"]

    reviewer_info = state["reviewer"]
    analyst_info = state["analyst"]

    questionnaire = state["team_questionnaire"]

    reviewer_name = state["reviewer"].name
    print(f"Reviewer {reviewer_name} from {team_name} activated.")

    system_prompt = reviewer_prompt.format(topic=topic,
                                          team = team_name + "\n" + team_description,
                                          analyst = analyst_info,
                                          person = reviewer_info,
                                          questionnaire = questionnaire)



    last_message = state["messages"][-1].content

    messages = [SystemMessage(content=system_prompt),
                last_message,
                ]


    return {"messages": [llm.invoke(messages).content]}
    # return {"messages": [AIMessage("Reviewers answer " + state["reviewer_prompt"][0:25])] + state.get("messages", [])} # For test


def should_continue(state: ResearchState):
    """
    Determines whether to proceed to the next step or end the workflow.

    If the number of messages reaches the defined threshold, the final review is appended to the
    "reviews" list in the state, and the workflow ends. Otherwise, it transitions to the reviewer node.

    Args:
        state (ResearchState): The current state of the research team containing:
            - "messages" (list): Previous messages exchanged in the workflow.
            - "reviews" (list): List of final reviews collected.

    Returns:
        str: Returns `END` if the workflow should end, or "Reviewer" for the next step.
    """
    messages = state.get("messages", [])
    # Check if the number of messages is 6 or more
    if len(messages) >= 7:

        # Return the END constant and the overall state update
        state["reviews"].append(messages[-1].content)
        return END

    # If the condition is not met, return the next node
    return "Reviewer"

