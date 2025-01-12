import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langgraph.constants import END

from graphHierarchicalTeams.states import SubordinateState
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


def subordinate_define_edge(state: SubordinateState):
    """
    Initializes states for each research team.
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
    Generates a list of research teams based on the given topic.
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


def subordinate_node(state: SubordinateState):
    """
    Supervisor node for orchestrating the research workflow.
    """
    # print("This is log info FROM SUPERVISOR about reviews list length: " + str(len(state["reviews"])))
    print("Subordinate Node has been activated!")

    if "reviews" not in state:
        state["reviews"] = []

    if "teams" not in state or not state["teams"]:
        # Generate teams and initialize states
        generated_teams = create_research_teams_tool.invoke({"topic": state["topic"]})
        state["teams"] = generated_teams["teams"]

    return state


# Example usage
# if __name__ == "__main__":
#     # Mock OverallState for demonstration
#     state = OverallState(topic="Digital Transformation in Organizations")
#
#     print("initial_state: ", json.dumps(state, indent=4, ensure_ascii=False))
#
#     # Invoke the model with the tools and initial state
#     supervisor_node(state)
#
#     # Print the updated state
#     print("update_state:", json.dumps(state, indent=4, ensure_ascii=False))
