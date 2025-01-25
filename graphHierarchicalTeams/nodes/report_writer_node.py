"""
Main module for generating a comprehensive report based on input data from subordinate states.

This script loads environment variables, initializes a language model, defines writing instructions,
and provides functionality to create a summarized report using the state of a subordinate.

Modules Used:
    - dotenv: For loading environment variables.
    - langchain_openai: To interact with OpenAI's chat models.
    - langchain_core.messages: To structure messages for language model interaction.
    - os: For accessing environment variables.
    - graphHierarchicalTeams.states: Custom module for defining subordinate states.

Functions:
    - report_writer_node: Generates a detailed report based on the subordinate state.

Environment Variables:
    - MODEL: The name of the model to be used by the language model.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
import os
from graphHierarchicalTeams.states import SubordinateState



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
    """
    Generate a comprehensive report based on the provided subordinate state.

    This function extracts information (topic, questionnaire, and reviews) from the subordinate state,
    formats it into a structured system message, and invokes a language model to generate a complete report.

    Args:
        state (SubordinateState): The current state object containing the following keys:
            - topic (str): The topic of the task.
            - questionnaire (str): The questionnaire details.
            - reviews (str): The reviews provided by the analyst-reviewer teams.

    Returns:
        SubordinateState: The updated state object with added or modified keys as necessary.
    """
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
