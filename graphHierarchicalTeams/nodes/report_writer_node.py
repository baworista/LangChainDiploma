from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
import os

from graphHierarchicalTeams.states import SubordinateState
from graphSupervisor.states import OverallState


load_dotenv()

llm = ChatOpenAI(model_name=os.getenv("MODEL"))

writing_instructions = """You are a senior consultant experienced in writing executive reports. Your goal is to write a comprehensive report based on the reviews provided by the analyst-reviewer teams.

The report should be structured, concise, and actionable. It should include an executive summary, an introduction, a detailed analysis, and a set of recommendations.

Here are the topic of task: {topic}

Here are the questionnaire: {questionnaire}

Here are reviews from teams: {reviews}.

Write a report from provided.
"""


def report_writer_node(state: SubordinateState):
    """ Node to summarize diagnosis and recommendations in a single report"""

    print("... Write Report ...")
    # Get state
    topic = state["topic"]
    questionnaire = state["questionnaire"]
    reviews = state["reviews"]

    # Generate question
    system_message = writing_instructions.format(topic=topic, questionnaire=questionnaire, reviews=reviews)
    report = llm.invoke([SystemMessage(content=system_message)])

    # Write messages to state
    return {"final_subordinate_report": report.content}
