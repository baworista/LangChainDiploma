from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from graphSupervisor.state import AnalystState
from graphSupervisor.state import OverallState

from auth_utils import auth_func

auth_func()

llm = ChatOpenAI(model_name='gpt-4o-mini', temperature=0)

def diagnose_tool(state:AnalystState):

    diagnosis_instructions = """You are an analyst tasked with needs analysis of Your customer.
    Here is Your detailed persona, including role in the projects, competencies and tasks: {goals}

    Your goal is diagnose the current state of the customer basing on questionnaire results.
    Here is the questionnaire results: {questionnaire}

    Generate only a diagnosis based on the questionnaire results. 
    Your diagnosis should solely focus on Your persona, competencies and tasks.
    Do not diagnose aspects outside of Your persona competencies.
    Do not recommend any solutions yet. 
    """

    analyst = state["analyst"]
    topic = state["topic"]
    print(f"Analyst: {analyst.name}")
    # print(f"Topic: {topic}")
    questionnaire = state.get("questionnaire", "Questionnaire results")  # Get questionnaire or use default

    # Generate diagnosis
    system_message = diagnosis_instructions.format(
        goals=analyst.persona,
        questionnaire=questionnaire
    )
    diagnosis_result = llm.invoke([SystemMessage(content=system_message)])
    print("... Diagnose end...")
    return {
        "diagnosis": [diagnosis_result.content]  # Store current diagnosis
    }

def recommend_tool(state: AnalystState)-> OverallState:
    recommendations_instructions = """You are an analyst tasked with helping Your customer in the {topic}.".
    Here is Your detailed persona, including role in the projects, competencies and tasks: {goals}

    Your goal is make constructive and interesting recommendations basing on an initial diagnosis.
    1. Constructive: Recommendations that are helpful and actionable.
    2. Specific: Recommendations that avoid generalities and include specific examples from the expert.
    3. Managable: Recommendations that are realistic and can be implemented by the customer.

    Here is the diagnosis: {diagnosis}

    Generate only recommendation grounded in the diagnosis.
    Your recommendation should solely be inline with Your persona, competencies, and tasks.
    Do not make recommendations in aspects outside of Your persona, competencies, and tasks.
    """

    """ Node to make recommendations based on the diagnosis """
    print("... Recommend start ...")
    # Get state
    analyst = state["analyst"]
    print(f"Analyst: {analyst.name}")
    topic = state['topic']
    # print(f"Topic: {topic}")
    diagnosis = state['diagnosis']

    # Generate question
    system_message = recommendations_instructions.format(topic=topic, goals=analyst.persona, diagnosis=diagnosis)
    recommendation = llm.invoke([SystemMessage(content=system_message)])
    # Write messages to state
    return {"recommendations": [recommendation.content]}


def analyst_node(state: AnalystState) -> AnalystState:
    """
    Processes an individual analyst's state and updates it with diagnosis and recommendations.

    Args:
        state (AnalystState): The specific state for the analyst.

    Returns:
        AnalystState: Updated state with diagnosis and recommendations.
    """
    print(f"Processing {state['analyst_name']}...")

    # Generate diagnosis
    diagnosis_result = diagnose_tool(state)
    state.update(diagnosis_result)

    # Generate recommendations
    recommendation_result = recommend_tool(state)
    state.update(recommendation_result)

    print(f"Completed analysis for {state['analyst_name']}")
    return state






# def analyst_node(topic: str, name: str, role: str, description: str) -> AnalystState:
#     """
#     Processes an individual analyst and generates their unique AnalystState.
#
#     Args:
#         topic (str): The topic of the analysis.
#         name (str): The name of the analyst.
#         role (str): The role of the analyst.
#         description (str): The description of the analyst's focus and tasks.
#
#     Returns:
#         AnalystState: The unique state for the processed analyst.
#     """
#     print(f"Processing {name}...")
#     print(f"Name: {name}")
#     print(f"Topic: {topic}")
#     print(f"Role: {role}")
#     print(f"Description: {description}")
#
#     # Create and return the unique AnalystState
#     analyst_state = {
#         "analyst_name": name,
#         "topic": topic,
#         "role": role,
#         "description": description,
#     }
#
#     print(f"Generated state for {name}:\n{analyst_state}")
#     return analyst_state


