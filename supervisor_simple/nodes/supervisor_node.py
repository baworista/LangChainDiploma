import json
import os

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send

from supervisor_simple.states import OverallState, Perspectives

# LLM Initialization
load_dotenv()
llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"), temperature=0)

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


def initialize_research_states(state: OverallState) -> list[Send]:
    """
    Initializes states for each research team.
    """
    topic = state["topic"]
    teams = state["teams"]

    return [
        Send(
            team["name"],
            {
                "topic": topic,  # Topic assigned to the analyst
                "description": team["description"],
                "questionnaire": "=====",
                "result": "",
                "current_iteration": 0,
                "max_iterations": 3,
                "analyst_prompt": team["analyst_prompt"],
                "reviewer_prompt": team["reviewer_prompt"],
            }
        ) for team in teams
    ]


@tool
def create_research_teams_tool(topic: str) -> dict:
    """
    Generates a list of research teams based on the given topic.
    """
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
            "analyst_prompt": team.analyst_prompt,
            "reviewer_prompt": team.reviewer_prompt,
        }
        for team in perspectives.teams
    ]

    return {"teams": serialized_teams}


# @tool
# def initialize_research_states(topic: str, teams: List[dict]) -> list[Send]:
#     """
#     Initializes states for each research team.
#     """
#
#     return [
#         Send(
#             team["name"],
#             {
#                 "topic": topic,  # Topic assigned to the analyst
#                 "description": team["description"],
#                 "questionnaire": "piska",
#                 "result": "",
#                 "current_iteration": 0,
#                 "max_iterations": 3,
#                 "analyst_prompt": team["analyst_prompt"],
#                 "reviewer_prompt": team["reviewer_prompt"],
#             }
#         ) for team in teams
#     ]


def supervisor_node(state: OverallState):
    """
    Supervisor node for orchestrating the research workflow.
    """
    if "teams" not in state or not state["teams"]:
        # Generate teams and initialize states
        generated_teams = create_research_teams_tool.invoke({"topic": state["topic"]})
        state["teams"] = generated_teams["teams"]

    return state


# Example usage
if __name__ == "__main__":
    # Mock OverallState for demonstration
    state = OverallState(topic="Digital Transformation in Organizations")

    print("initial_state: ", json.dumps(state, indent=4, ensure_ascii=False))

    # Invoke the model with the tools and initial state
    supervisor_node(state)

    # Print the updated state
    print("update_state:", json.dumps(state, indent=4, ensure_ascii=False))
