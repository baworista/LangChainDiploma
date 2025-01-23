"""
Module for managing the workflow of analysts and reviewers in a hierarchical team.

This module provides functionality for:
- Activating the `Analyst` node to perform a needs analysis.
- Activating the `Reviewer` node to provide constructive feedback on the analysis.
- Determining whether the workflow should continue or transition to the final state.

It uses language models to generate analysis and reviews based on structured prompts and manages the state of the research process.

Modules Used:
    - os: For accessing environment variables.
    - langchain_core.messages: For managing system messages.
    - langchain_openai: For interacting with OpenAI's language model.
    - langgraph.constants: For workflow state management (e.g., `END`).
    - graphHierarchicalTeams.states: For managing the research state.

Functions:
    - analyst_node: Activates the analyst node to generate a needs analysis based on the questionnaire results.
    - reviewer_node: Activates the reviewer node to provide feedback on the analysis.
    - should_continue: Determines whether the workflow should transition to the final state or proceed.

Constants:
    - analyst_prompt: Template for the analyst's role, context, and guidelines.
    - reviewer_prompt: Template for the reviewer's role, context, and guidelines.
"""

import os
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import END

from graphHierarchicalTeams.states import ResearchState


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
    Activate the analyst node to perform a needs analysis.

    The analyst analyzes the current state of the customer based on the provided questionnaire results
    and, if available, integrates feedback from the reviewer.

    Args:
        state (dict): The current state of the process containing the following keys:
            - "team_topic" (str): The topic assigned to the team.
            - "team_name" (str): The name of the team.
            - "description" (str): A description of the team and its responsibilities.
            - "reviewer" (str): Information about the reviewer in the team.
            - "analyst" (str): Information about the analyst in the team.
            - "team_questionnaire" (str): The questionnaire results to be analyzed.
            - "messages" (list): A list of previous messages in the conversation.

    Returns:
        ResearchState: A dictionary containing updated messages after invoking the language model.
    """
    topic = state["team_topic"]

    team_name = state["team_name"]
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


def reviewer_node(state):
    """
    Activate the reviewer node to provide feedback on the analyst's analysis.

    The reviewer creates constructive and actionable recommendations based on the analyst's analysis
    and the provided questionnaire results.

    Args:
        state (dict): The current state of the process containing the following keys:
            - "team_topic" (str): The topic assigned to the team.
            - "team_name" (str): The name of the team.
            - "description" (str): A description of the team and its responsibilities.
            - "reviewer" (str): Information about the reviewer in the team.
            - "analyst" (str): Information about the analyst in the team.
            - "team_questionnaire" (str): The questionnaire results to be analyzed.
            - "messages" (list): A list of previous messages in the conversation.

    Returns:
        dict: A dictionary containing updated messages after invoking the language model.
    """
    topic = state["team_topic"]

    team_name = state["team_name"]
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


def should_continue(state: ResearchState):
    """
    Determine whether the workflow should continue or transition to the final state.

    If the number of messages reaches the defined limit, appends the last message
    to the reviews list and ends the workflow. Otherwise, transitions to the next node.

    Args:
        state (ResearchState): The current research state containing the following keys:
            - "messages" (list): A list of messages exchanged in the workflow.
            - "reviews" (list): A list to store final reviews.

    Returns:
        str: Returns `END` if the workflow should end; otherwise, transitions to "Reviewer".
    """
    messages = state.get("messages", [])
    # Check if the number of messages is 6 or more
    if len(messages) >= 5:

        # Return the END constant and the overall state update
        state["reviews"].append(messages[-1].content)
        return END

    # If the condition is not met, return the next node
    return "Reviewer"

