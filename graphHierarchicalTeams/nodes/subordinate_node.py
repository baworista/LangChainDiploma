"""
Main module for managing AI research teams and orchestrating their workflows.

This module provides tools and functions to define research teams, manage their states, and generate comprehensive reports.
It utilizes a language model for team generation and report writing, based on structured prompts and state transitions.

Modules Used:
    - os: For accessing environment variables.
    - dotenv: To load environment variables from a `.env` file.
    - langchain.tools: To define tools within the LangChain framework.
    - langchain_core.messages: For structuring messages for the language model.
    - langchain_openai: For interacting with OpenAI's chat models.
    - langgraph.constants: For using `Send` and `END` constants in the workflow.
    - graphHierarchicalTeams.states: For managing subordinate states.
    - graphHierarchicalTeams.schema: For defining the `Perspectives` schema.

Environment Variables:
    - MODEL_SUPERVISOR: Specifies the language model used for the supervisor tool.

Functions:
    - subordinate_define_edge: Defines the workflow edge for subordinate state transitions.
    - create_research_teams_tool: Generates a list of research teams based on the given topic and structured instructions.
    - subordinate_node: Acts as a supervisor node, managing the research workflow and team orchestration.

Constants:
    - team_creation_instructions: Instructions for generating research teams.
    - inside_processes_teams_info: Team definitions for inside processes.
    - outside_processes_teams_info: Team definitions for outside processes.
"""

import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langgraph.constants import END
from graphHierarchicalTeams.states import SubordinateState
from graphHierarchicalTeams.schema import Perspectives



load_dotenv()
llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))

team_creation_instructions = """
You are tasked with creating AI research teams, each consisting of an analyst and a reviewer. Follow these instructions:
Use provided in prompts names
1. Review the provided research topic.
2. Generate research teams strictly using provided names:
    {teams_info}
3. Each team must have explicitly provided name, description and prompts reflecting their responsibilities.
"""

inside_processes_teams_info = """
    a. HR_Team: Focused on HR issues like team dynamics, performance, and training.
    b. BP_Team: Specializing in process optimization and automation.
    c. KM_Team: Concentrating on knowledge sharing and tools.
    d. IT_Team: Addressing IT strategies and tools.
    There are 4 teams in total.
"""

outside_processes_teams_info = """
    a. Marketing_Team: Focused on market research, brand awareness, customer acquisition, and promotional strategies.
    b. Finance_Team: Specializing in financial planning, budgeting, analysis of profitability, investment strategies, and risk management.  
    c. Legal_Team: Concentrating on ensuring compliance with laws and regulations, drafting contracts, managing legal risks, and providing legal counsel.
    d. Customer_Support_Team: Addressing customer inquiries, feedback, and resolving issues to ensure a positive customer experience and maintain satisfaction.
    e. R&D_Team: Focused on innovation, developing new products or services, researching emerging technologies, and driving long-term business growth through product advancements.
    There are 5 teams in total.
"""

def subordinate_define_edge(state: SubordinateState):
    """
    Define the next workflow state for subordinate nodes based on the current state.

    Args:
        state (SubordinateState): The current state object containing the following keys:
            - "final_subordinate_report" (str, optional): The final report, if available.
            - "reviews" (list): A list of reviews from teams.
            - "topic" (str): The research topic.
            - "teams" (list): A list of team details.
            - "questionnaire" (str): The questionnaire associated with the task.

    Returns:
        str or list: Returns `END` if the final report is available, a string `"Report_Writer"` if sufficient reviews exist,
        or a list of `Send` objects to initialize team states.
    """
    if "final_subordinate_report" in state:
        return END

    if len(state["reviews"]) >= 4:
        return "Report_Writer"

    topic = state["topic"]
    teams = state["teams"]
    questionnaire = state["questionnaire"]

    print(f"Initializing research teams for topic: \n\t{topic}")

    return [
        Send(
            team["team_name"],
            {
                "team_name": team["team_name"],
                "team_topic": topic,  # Topic assigned to the analyst
                "description": team["description"],
                "team_questionnaire": questionnaire,
                "messages": [],
                "reviews": [],
                "subordinate_reviews": [],
                "analyst": team["analyst"],
                "reviewer": team["reviewer"],
            }
        ) for team in teams
    ]


@tool
def create_research_teams_tool(topic: str, team_info: str) -> dict:
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
    system_prompt = team_creation_instructions.format(teams_info=team_info)
    system_message = SystemMessage(content=system_prompt)
    human_message = HumanMessage(content=f"Generate the teams for the topic: {topic}.")

    # Teams generation
    perspectives: Perspectives = structured_llm.invoke([system_message, human_message])

    # Serialize
    serialized_teams = [
        {
            "team_name": team.name,
            "description": team.description,
            "analyst": team.analyst,
            "reviewer": team.reviewer,
        }
        for team in perspectives.teams
    ]

    return {"teams": serialized_teams}


def subordinate_node(state: SubordinateState):
    """
    Orchestrate the workflow for subordinate nodes by generating teams and handling reports.

    Args:
        state (SubordinateState): The current state object containing the following keys:
            - "teams" (list, optional): A list of team details.
            - "subordinate_team_name" (str): The name of the subordinate team.
            - "topic" (str): The research topic.
            - "final_subordinate_report" (str, optional): The final report, if available.
            - "subordinate_reviews" (list): A list of subordinate reviews.

    Returns:
        SubordinateState: The updated state object with added or modified keys as necessary.
    """
    print("Subordinate Node has been activated!")

    if "teams" not in state or not state["teams"]:
        # Generate teams and initialize states
        curr_team = state["subordinate_team_name"]
        if curr_team.startswith("Inside_Processes"):
            generated_teams = create_research_teams_tool.invoke({"topic": state["topic"], "team_info": inside_processes_teams_info})
        if curr_team.startswith("Outside_Processes"):
            generated_teams = create_research_teams_tool.invoke({"topic": state["topic"], "team_info": outside_processes_teams_info})
        state["teams"] = generated_teams["teams"]

    if "final_subordinate_report" in state:
        report = state["final_subordinate_report"]
        state["subordinate_reviews"].append(report)

    return state
