import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Send

from graphNetwork.schemas import Perspectives
from graphNetwork.states import OverallState


load_dotenv()
llm = ChatOpenAI(model_name=os.getenv("MODEL"))

agents_creation_instructions = """
You are tasked with creating AI agents-analysts. Follow these instructions:
Use provided in prompts names
1. Review the provided research topic.
2. Generate four research teams strictly using provided names:
    a. **HR_Agent**: Focused on HR issues like team dynamics, performance, and training.
    b. **BP_Agent**: Specializing in process optimization and automation.
    c. **KM_Agent**: Concentrating on knowledge sharing and tools.
    d. **IT_Agent**: Addressing IT strategies and tools.
3. Each agent must have explicitly provided name, role and description reflecting their responsibilities.
"""

def initialize_agents_from_state(state: OverallState):
    """
    Initializes agents based on the provided overall state.
    Combines agent creation and initialization.
    """
    topic = state["topic"]
    questionnaire = state["questionnaire"]
    questionnaire = "Here should be questions, but now this is just a test!"

    print(f"Initializing agents for topic:\n\t{topic}")

    # Use LLM to generate structured agent configurations
    structured_llm = llm.with_structured_output(Perspectives)
    system_message = SystemMessage(content=agents_creation_instructions)
    human_message = HumanMessage(content=f"Generate the agents for the topic: {topic}.")

    # Generate agent configurations
    perspectives: Perspectives = structured_llm.invoke([system_message, human_message])

    # Serialize agent data
    serialized_agents = [
        {
            "code_name": agent.code_name,
            "name": agent.name,
            "role": agent.role,
            "description": agent.description
        }
        for agent in perspectives.agents
    ]

    # Return initialized agents (could also return "Send" objects if needed)
    return [
        Send(
            agent["code_name"],
            {
                "code_name": agent["code_name"],
                "name": agent["name"],
                "description": agent["description"],
                "role": agent["role"],
                "agent_topic": topic,
                "agent_questionnaire": questionnaire,
                "messages": [],
                "current_analysis": "",
                "questions_asked": 0,
            }
        )
        for agent in serialized_agents
    ]