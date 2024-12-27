from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.types import Send

from graphNetwork.states import OverallState


load_dotenv()
llm = ChatOpenAI(model_name="MODEL")

def initialize_agents_from_state(state: OverallState):
    """
    Initializes agents based on the provided overall state.
    Combines agent creation and initialization.
    """
    topic = state["topic"]
    questionnaire = state["questionnaire"]
    teams = state["teams"]  # Assumes this contains basic agent-related info.

    print(f"Initializing agents for topic:\n\t{topic}")

    # # Use LLM to generate structured agent configurations
    # structured_llm = llm.with_structured_output(Perspectives)
    # system_message = SystemMessage(content=team_creation_instructions)
    # human_message = HumanMessage(content=f"Generate the agents for the topic: {topic}.")
    #
    # # Generate agent configurations
    # perspectives: Perspectives = structured_llm.invoke([system_message, human_message])

    # # Serialize agent data
    # serialized_agents = [
    #     {
    #         "name": agent.name,
    #         "description": agent.description,
    #         "analyst": agent.analyst,
    #         "reviewer": agent.reviewer,
    #     }
    #     for agent in perspectives.teams
    # ]

    # # Update state with agents and initialize their details
    # state["agents"] = [
    #     {
    #         "name": agent["name"],
    #         "agent_topic": topic,  # Topic assigned to the agent
    #         "description": agent["description"],
    #         "agent_questionnaire": questionnaire,
    #         "messages": [],
    #         "reviews": [],
    #         "analyst": agent["analyst"],
    #         "reviewer": agent["reviewer"],
    #     }
    #     for agent in serialized_agents
    # ]

    # Return initialized agents (could also return "Send" objects if needed)
    return [
        Send(
            agent["name"],
            {
                "name": agent["name"],
                "agent_topic": agent["agent_topic"],
                "description": agent["description"],
                "agent_questionnaire": agent["agent_questionnaire"],
                "messages": [],
                "reviews": [],
                "analyst": agent["analyst"],
                "reviewer": agent["reviewer"],
            }
        )
        for agent in state["agents"]
    ]