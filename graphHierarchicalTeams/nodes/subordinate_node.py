import os
from idlelib.undo import Command

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langgraph.constants import END
from sqlalchemy.orm.sync import update

from graphHierarchicalTeams.states import SubordinateState
from graphSupervisor.states import OverallState, Perspectives


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
"""

outside_processes_teams_info = """
    a. Marketing_Team: Focused on market research, brand awareness, customer acquisition, and promotional strategies.
    b. Finance_Team: Specializing in financial planning, budgeting, analysis of profitability, investment strategies, and risk management.  
    c. Legal_Team: Concentrating on ensuring compliance with laws and regulations, drafting contracts, managing legal risks, and providing legal counsel.
    d. Customer_Support_Team: Addressing customer inquiries, feedback, and resolving issues to ensure a positive customer experience and maintain satisfaction.
    e. R&D_Team: Focused on innovation, developing new products or services, researching emerging technologies, and driving long-term business growth through product advancements.
"""

def subordinate_define_edge(state: SubordinateState):
    """
    Initializes states for each research team.
    """
    # print("This is log info FROM DEFINE_EDGE about reviews list length: " + str(len(state["reviews"])))

    if "final_subordinate_report" in state:
        report = state["final_subordinate_report"]
        state["subordinate_reviews"].append(report)
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
                "analyst": team["analyst"],
                "reviewer": team["reviewer"],
            }
        ) for team in teams
    ]


@tool
def create_research_teams_tool(topic: str, team_info: str) -> dict:
    """
    Generates a list of research teams based on the given topic.
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
    Supervisor node for orchestrating the research workflow.
    """
    # print("This is log info FROM SUPERVISOR about reviews list length: " + str(len(state["reviews"])))
    print("Subordinate Node has been activated!")

    if "reviews" not in state:
        state["reviews"] = []

    if "teams" not in state or not state["teams"]:
        # Generate teams and initialize states
        curr_team = state["subordinate_team_name"]
        if curr_team.startswith("Inside_Processes"):
            generated_teams = create_research_teams_tool.invoke({"topic": state["topic"], "team_info": inside_processes_teams_info})
        if curr_team.startswith("Outside_Processes"):
            generated_teams = create_research_teams_tool.invoke({"topic": state["topic"], "team_info": outside_processes_teams_info})
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
