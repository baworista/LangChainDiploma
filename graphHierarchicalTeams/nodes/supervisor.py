import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langgraph.types import Command
from langgraph.constants import END

from graphHierarchicalTeams.schema import Perspectives, Subordinates
from graphHierarchicalTeams.states import OverallState

load_dotenv()
llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))


subordinates_creation_instructions = """
You are main supervisor in hierarchical architecture network. You are responsible for creating subordinates.
Use provided in prompts names
1. Review the provided research topic.
2. Generate two subordinate teams strictly using provided names:
    a. **Inside_Processes_Team**: his team will consist of it's subordinate, HR_Team, BP_Team, KM_Team, IT_Team and responsible for internal processes.
    b. **Outside_Processes_Team**: his team will consist of it's subordinate, Sales_Team, Marketing_Team, PR_Team, Support_Team and responsible for external processes.
3. Each subordinate supervisor must have explicitly provided name, description and prompts reflecting their responsibilities.
"""


@tool
def create_subordinates_tool(topic: str) -> dict:
    """
    Generates a list of research teams based on the given topic.
    """

    print(f"Creating subordinates on topic: \n\t{topic}")
    structured_llm = llm.with_structured_output(Subordinates)

    # LLM Query
    system_message = SystemMessage(content=subordinates_creation_instructions)
    human_message = HumanMessage(content=f"Generate subordinates for the topic: {topic}.")

    # Teams generation
    subordinates: Subordinates = structured_llm.invoke([system_message, human_message])

    # Serialize
    serialized_subordinates = [
        {
            "name": subordinate.name,
            "role": subordinate.role,
            "description": subordinate.description,
        }
        for subordinate in subordinates.subordinates
    ]

    print("Serialized subordinates created!" + str(serialized_subordinates))
    return {"subordinates": serialized_subordinates}


def supervisor_define_edge(state: OverallState):
    """
    Send the state to the subordinate.
    """

    topic = state["topic"]
    subordinates = state["subordinates"]
    questionnaire = state["questionnaire"]

    print(f"Initializing subordinates for topic: \n\t{topic}")

    return [
        Send(
            subordinate["name"],
            {
                'topic': topic,
                'questionnaire': subordinates,
                'subordinates': subordinates,
            }
        ) for subordinate in subordinates
    ]


def superivisor_node(state: OverallState):
    """
    Main supervisor node for orchestrating the research workflow.
    """
    if "subordinates" not in state or not state["subordinates"]:
        # Generate teams and initialize states
        generated_subordinates = create_subordinates_tool.invoke({"topic": state["topic"]})
        state["subordinates"] = generated_subordinates["subordinates"]
        print("Subordinates created and added in state!")

    return state