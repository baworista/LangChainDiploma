import json
from typing import List

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from supervisor_simple.states import OverallState, ResearchState, Perspectives

# LLM Initialization
load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

team_creation_instructions = """
You are tasked with creating AI research teams, each consisting of an analyst and a reviewer. Follow these instructions:

1. Review the provided research topic.
2. Generate four research teams:
    a. Human Resources Team: Focused on HR issues like team dynamics, performance, and training.
    b. Business Process Team: Specializing in process optimization and automation.
    c. Knowledge Management Team: Concentrating on knowledge sharing and tools.
    d. IT Systems Team: Addressing IT strategies and tools.
3. Each team must have a detailed name, description and prompts reflecting their responsibilities.
"""


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


@tool
def initialize_research_states(topic: str, teams: List[dict]):
    """
    Initializes states for each research team.
    """

    teams_states = []
    for idx, team in enumerate(teams):
        research_state = ResearchState(
            research_id=idx + 1,
            research_name=team["name"],
            topic=topic,
            questionnaire="",
            messages=[],  # Empty conversation history initially
            result="",
            analyst_prompt=f"Analyst: {team['description']}",
            reviewer_prompt=f"Reviewer: {team['description']}",
        )
        teams_states.append(research_state)

    return {"teams_states": teams_states}


def supervisor_node(state: OverallState):
    """
    Supervisor node for orchestrating the research workflow.
    """
    if "teams_states" not in state or not state["teams_states"]:
        # Generate teams and initialize states
        generated_teams = create_research_teams_tool.invoke({"topic": state["topic"]})
        state["teams"] = generated_teams["teams"]

        initialize_research_states.invoke({"topic": state["topic"], "teams": state["teams"]})

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
