import os
from typing import List
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langgraph.constants import END

from graphHierarchicalTeams.schema import Subordinates
from graphHierarchicalTeams.states import OverallState

"""
Main module for managing the hierarchical architecture network, including the creation of subordinate teams
and the generation of comprehensive reports.

This module enables the orchestration of workflows for a hierarchical system, where the main supervisor node
oversees subordinate teams. It provides tools for creating teams, managing their states, and compiling final reports
based on team reviews.

Modules Used:
    - os: For accessing environment variables.
    - typing: For type annotations (e.g., List).
    - dotenv: To load environment variables from a `.env` file.
    - langchain.tools: To define tools within the LangChain framework.
    - langchain_core.messages: For structuring messages for language model interactions.
    - langchain_openai: For interacting with OpenAI's chat models.
    - langgraph.constants: For constants used in workflow orchestration (`Send`, `END`).
    - graphHierarchicalTeams.schema: For defining subordinate schema (`Subordinates`).
    - graphHierarchicalTeams.states: For managing overall hierarchical state (`OverallState`).

Environment Variables:
    - MODEL_SUPERVISOR: Specifies the language model used for the supervisor tool.

Functions:
    - create_subordinates_tool: Generates subordinate teams based on the given topic.
    - report_writer_tool: Generates a structured report based on the provided reviews.
    - supervisor_define_edge: Defines the next workflow state based on the overall state.
    - superivisor_node: The main node managing the hierarchical workflow, creating teams and compiling the final report.

Constants:
    - subordinates_creation_instructions: Instructions for creating subordinate teams.
    - writing_instructions: Guidelines for generating structured reports.
"""

load_dotenv()
llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))


subordinates_creation_instructions = """
You are main supervisor in hierarchical architecture network. You are responsible for creating subordinate teams.
Use provided in prompts names
1. Review the provided research topic.
2. Generate two subordinate teams strictly using provided names:
    a. **Inside_Processes_Team**: this team will consist of it's subordinate supervisor and other little teams responsible for internal processes.
    b. **Outside_Processes_Team**: this team will consist of it's subordinate supervisor and other little teams responsible for external processes.
3. Each subordinate team must have explicitly provided name, description and prompts reflecting their responsibilities.
"""

writing_instructions = """You are a senior consultant experienced in writing executive reports. Your goal is to write a comprehensive report based on the reviews provided by the analyst-reviewer teams.

The report should be structured, concise, and actionable. It should include an executive summary, an introduction, a detailed analysis, and a set of recommendations.

Here are the topic of task: {topic}

Here are the questionnaire: {questionnaire}

Here are reviews from teams: {reviews}.

Write a report from provided.
"""


@tool
def create_subordinates_tool(topic: str) -> dict:
    """
    Generates subordinate teams based on the given topic.

    This tool uses a structured language model to create two subordinate teams: `Inside_Processes_Team`
    and `Outside_Processes_Team`, each with its own description and responsibilities.

    Args:
        topic (str): The research topic for which subordinate teams are to be created.

    Returns:
        dict: A dictionary containing the serialized subordinate teams with the following keys:
            - "subordinate_team_name" (str): The name of the subordinate team.
            - "description" (str): A brief description of the subordinate team's purpose.
            - "subordinate" (list): A list of subordinates in the team.
    """

    print(f"Creating subordinate teams on topic: \n\t{topic}")
    structured_llm = llm.with_structured_output(Subordinates)

    # LLM Query
    system_message = SystemMessage(content=subordinates_creation_instructions)
    human_message = HumanMessage(content=f"Generate subordinate teams for the topic: {topic}.")

    # Teams generation
    subordinate_teams: Subordinates = structured_llm.invoke([system_message, human_message])

    # Serialize
    serialized_subordinate_teams = [
        {
            "subordinate_team_name": subordinate_team.name,
            "description": subordinate_team.description,
            "subordinate": subordinate_team.subordinate,
        }
        for subordinate_team in subordinate_teams.subordinates
    ]

    print("Serialized subordinates created!" + str(serialized_subordinate_teams))
    return {"subordinate_teams": serialized_subordinate_teams}


@tool
def report_writer_tool(topic: str, questionnaire, reviews: List[str]):
    """
    Generates a comprehensive report based on reviews from subordinate teams.

    This tool compiles the input topic, questionnaire, and reviews into a structured executive report.

    Args:
        topic (str): The topic of the task.
        questionnaire (str): The questionnaire related to the task.
        reviews (List[str]): A list of reviews from subordinate teams.

    Returns:
        dict: A dictionary containing the final report content.
    """
    print("Main supervisor's report tool has been activated!")
    # Generate question
    system_message = writing_instructions.format(topic=topic, questionnaire=questionnaire, reviews=reviews)
    report = llm.invoke([SystemMessage(content=system_message)])

    # Write messages to state
    return report


def supervisor_define_edge(state: OverallState):
    """
    Defines the next workflow step for the supervisor node.

    If the final report is already in the state, the workflow ends. Otherwise, it initializes
    subordinate teams and transitions to their states.

    Args:
        state (OverallState): The current overall state containing the following keys:
            - "final_report" (str, optional): The final report, if available.
            - "topic" (str): The research topic.
            - "questionnaire" (str): The questionnaire related to the task.
            - "subordinate_teams" (list): A list of subordinate team details.

    Returns:
        str or list: Returns `END` if the final report is available, or a list of `Send` objects
                     to transition to subordinate states.
    """

    if "final_report" in state:
        return END

    topic = state["topic"]
    questionnaire = state["questionnaire"]
    subordinate_teams = state["subordinate_teams"]

    print(f"Initializing subordinate teams for topic: \n\t{topic}")

    return [
        Send(
            subordinate_team["subordinate_team_name"],
            {
                'topic': topic,
                'questionnaire': questionnaire,
                'subordinate_team_name': subordinate_team["subordinate_team_name"],
                'subordinate_reviews': [],
                'description': subordinate_team["description"],
                'subordinate': subordinate_team['subordinate'],
            }
        ) for subordinate_team in subordinate_teams
    ]


def superivisor_node(state: OverallState):
    """
    Main node for orchestrating the hierarchical research workflow.

    This function manages the workflow by generating subordinate teams, overseeing their processes,
    and compiling a final report based on subordinate reviews.

    Args:
        state (OverallState): The current overall state containing the following keys:
            - "subordinate_teams" (list, optional): A list of subordinate team details.
            - "topic" (str): The research topic.
            - "questionnaire" (str): The questionnaire related to the task.
            - "subordinate_reviews" (list): A list of reviews from subordinate teams.
            - "final_report" (str, optional): The final report, if available.

    Returns:
        OverallState: The updated state object with added or modified keys as necessary.
    """
    if "subordinate_teams" not in state or not state["subordinate_teams"]:
        # Generate teams and initialize states
        generated_subordinates = create_subordinates_tool.invoke({"topic": state["topic"]})
        state["subordinate_teams"] = generated_subordinates["subordinate_teams"]
        print("Subordinate teams created and added in state!")

    print("*" * 50)
    print("Main supervisor's subordinate reviews")
    print(state["subordinate_reviews"])
    print("*" * 50)
    if len(state["subordinate_reviews"]) >= 2:
        state.update({"final_report": report_writer_tool.invoke(
            {"topic": state["topic"], "questionnaire": state["questionnaire"],
             "reviews": state["subordinate_reviews"]})})

    return state