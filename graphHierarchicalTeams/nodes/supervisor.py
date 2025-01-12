import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langgraph.types import Command
from langgraph.constants import END

from graphHierarchicalTeams.schema import Perspectives, Subordinates, SubordinateTeam
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
            "name": subordinate_team.name,
            "description": subordinate_team.description,
            "subordinate": subordinate_team.subordinate,
        }
        for subordinate_team in subordinate_teams.subordinates
    ]

    print("Serialized subordinates created!" + str(serialized_subordinate_teams))
    return {"subordinate_teams": serialized_subordinate_teams}


def supervisor_define_edge(state: OverallState):
    """
    Send the state to the subordinate.
    """

    topic = state["topic"]
    questionnaire = state["questionnaire"]
    subordinate_teams = state["subordinate_teams"]

    print(f"Initializing subordinate teams for topic: \n\t{topic}")

    return [
        Send(
            subordinate_team["name"],
            {
                'topic': topic,
                'questionnaire': questionnaire,
                'name': subordinate_team["name"],
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

    return state