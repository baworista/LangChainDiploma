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
    Generates a list of research teams based on the given topic.
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
    Write a report based on the provided reviews.
    :param topic:
    :param questionnaire:
    :param reviews:
    :return:
    """
    print("Main supervisor's report tool has been activated!")
    # Generate question
    system_message = writing_instructions.format(topic=topic, questionnaire=questionnaire, reviews=reviews)
    report = llm.invoke([SystemMessage(content=system_message)])

    # Write messages to state
    return report


def supervisor_define_edge(state: OverallState):
    """
    Send the state to the subordinate.
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
    Main supervisor node for orchestrating the research workflow.
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