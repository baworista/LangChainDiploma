"""
Main module for managing the hierarchical architecture network, including the creation of subordinate teams and the generation of comprehensive reports.

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

writing_instructions = """
You are the Main Supervisor in a hierarchical organizational architecture overseeing two subordinates. Each subordinate is responsible for distinct operational domains:  
- Inside Processes: HR, Business Processes (BP), Knowledge Management (KM), and IT.  
- Outside Processes: Marketing, Finance, Legal, Customer Support, and Research & Development (R&D).  

Your subordinates have gathered detailed research and insights from their respective teams. Your responsibility is to synthesize their input into a comprehensive report that provides a clear, actionable analysis.

The report should be structured professionally, including:  
1. Executive Summary: A high-level overview of the findings and key takeaways.  
2. Introduction: Context and purpose of the report, including the scope of the analysis.  
3. Detailed Analysis: A deep dive into the research findings, categorizing insights by "Inside Processes" and "Outside Processes." Highlight key trends, challenges, and opportunities.  
4. Recommendations: Actionable steps and strategic suggestions based on the findings.

### Context:
- Topic of the Task: {topic}  
- Questionnaire: {questionnaire}  
- Research Findings from Teams: {reviews}  

Use the provided information to create a structured, insightful report. Ensure the tone is professional and the content is both concise and actionable.
"""


@tool
def create_subordinates_tool(topic: str) -> dict:
    """
    Generate subordinate teams based on the given topic.

    Args:
        topic (str): The research topic for which subordinate teams are to be created.

    Returns:
        dict: A dictionary containing the serialized subordinate teams with the following keys:
            - "subordinate_team_name" (str): Provided in system message subordinate team name.
            - "description" (str): Short description of what this team is response for..
            - "subordinate" (Person): Subordinate supervisor person
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
    Generate a comprehensive report based on reviews from subordinate teams.

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
    Define the next workflow step for the supervisor node.

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
    Orchestrate the hierarchical research workflow.

    Manage the workflow by generating subordinate teams, overseeing their processes,
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