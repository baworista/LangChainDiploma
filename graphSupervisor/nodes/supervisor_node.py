"""
Module for managing the research workflow by creating research teams and orchestrating their processes.

This module is designed for a supervisor to generate research teams based on a given topic,
initialize their states, and manage transitions between states as part of a supervisor workflow.

Key Features:
- Create research teams using a language model with structured outputs.
- Initialize research team states with predefined instructions.
- Orchestrate the research workflow by transitioning between nodes based on conditions.

Modules Used:
    - os: For accessing environment variables.
    - dotenv: For loading environment variables from a `.env` file.
    - langchain.tools: For defining tools within LangChain.
    - langchain_core.messages: For managing system and human messages.
    - langchain_openai: For interacting with OpenAI's language model.
    - langgraph.constants: For workflow state constants (`Send`, `END`).
    - graphSupervisor.states: For managing the `OverallState` and `Perspectives` schema.

Functions:
    - define_edge: Defines transitions between research team states.
    - create_research_teams_tool: Creates research teams based on the given topic using a language model.
    - supervisor_node: Orchestrates the workflow by generating teams and updating the overall state.

Constants:
    - team_creation_instructions: Instructions for generating research teams using the language model.
"""

import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langgraph.constants import END

from graphSupervisor.states import OverallState, Perspectives


load_dotenv()
llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))

team_creation_instructions = """
You are tasked with creating AI research teams, each consisting of an analyst and a reviewer. Follow these instructions:
Use provided in prompts names
1. Review the provided research topic.
2. Generate four research teams strictly using provided names:
    a. **HR_Team**: Focused on HR issues like team dynamics, performance, and training.
    b. **BP_Team**: Specializing in process optimization and automation.
    c. **KM_Team**: Concentrating on knowledge sharing and tools.
    d. **IT_Team**: Addressing IT strategies and tools.
3. Each team must have explicitly provided name, description and prompts reflecting their responsibilities.
"""


def define_edge(state: OverallState):
    """
    Define transitions between research team states based on the current state.

    If the final report is already generated, the workflow ends. Otherwise, transitions
    are defined based on the number of reviews and the presence of teams in the state.

    Args:
        state (OverallState): The current overall state, which includes:
            - "final_report" (str, optional): The final report, if available.
            - "reviews" (list): A list of reviews from the research teams.
            - "topic" (str): The research topic.
            - "teams" (list): A list of research team details.
            - "questionnaire" (str): The questionnaire data associated with the topic.

    Returns:
        str or list: Returns `END` if the final report is generated, or transitions to the
                     appropriate node based on conditions.
    """
    # print("This is log info FROM DEFINE_EDGE about reviews list length: " + str(len(state["reviews"])))

    if "final_report" in state:
        return END

    if len(state["reviews"]) >= 4:
        return "Report_Writer"

    topic = state["topic"]
    teams = state["teams"]
    questionnaire = state["questionnaire"]

    print(f"Initializing research teams for topic: \n\t{topic}")

    return [
        Send(
            team["name"],
            {
                "name": team["name"],
                "team_topic": topic,  # Topic assigned to the analyst
                "description": team["description"],
                "team_questionnaire": questionnaire,
                "messages": [],
                "reviews": [],
                "analyst": team["analyst"],
                "reviewer": team["reviewer"],
            }
        ) for team in teams
    ]


@tool
def create_research_teams_tool(topic: str) -> dict:
    """
    Create a list of research teams for a given topic using structured language model outputs.

    Args:
        topic (str): The research topic to base the teams on.

    Returns:
        dict: A dictionary containing the generated research teams with the following keys:
            - "name" (str): The name of the team.
            - "description" (str): A description of the team's responsibilities.
            - "analyst" (Person): The analyst assigned to the team.
            - "reviewer" (Person): The reviewer assigned to the team.
    """
    print(f"Creating research teams on topic: \n\t{topic}")
    structured_llm = llm.with_structured_output(Perspectives)

    # LLM Query
    system_message = SystemMessage(content=team_creation_instructions)
    human_message = HumanMessage(content=f"Generate the teams for the topic: {topic}.")

    # Teams generation
    perspectives: Perspectives = structured_llm.invoke([system_message, human_message])

    # Serialize
    serialized_teams = [
        {
            "name": team.name,
            "description": team.description,
            "analyst": team.analyst,
            "reviewer": team.reviewer,
        }
        for team in perspectives.teams
    ]

    return {"teams": serialized_teams}


def supervisor_node(state: OverallState):
    """
    Orchestrate the workflow for the research process.

    This function initializes the overall state, generates research teams if not already present,
    and manages transitions based on the state.

    Args:
        state (OverallState): The current overall state, which includes:
            - "topic" (str): The research topic.
            - "reviews" (list, optional): A list of reviews from research teams.
            - "teams" (list, optional): A list of research teams.

    Returns:
        OverallState: The updated overall state with initialized teams and reviews.
    """
    # print("This is log info FROM SUPERVISOR about reviews list length: " + str(len(state["reviews"])))

    if "reviews" not in state:
        state["reviews"] = []

    if "teams" not in state or not state["teams"]:
        # Generate teams and initialize states
        generated_teams = create_research_teams_tool.invoke({"topic": state["topic"]})
        state["teams"] = generated_teams["teams"]

    return state
