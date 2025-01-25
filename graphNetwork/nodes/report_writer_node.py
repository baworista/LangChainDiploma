"""
Module for generating a comprehensive summary report in the network workflow.

This module provides functionality to generate a final report that consolidates diagnoses
and recommendations based on the workflow's current state. It utilizes a language model
to generate structured and actionable insights.

Modules Used:
    - os: For managing environment variables.
    - langchain_core.messages: For creating system messages to interact with the language model.
    - langchain_openai: For interacting with OpenAI's language model.
    - graphNetwork.prompts.generators: For generating the prompt specific to the summary agent.
    - graphNetwork.states: For accessing the `OverallState` class representing the workflow state.

Function:
    - report_writer_node: Generates the final report based on the current workflow state.
"""

import os
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from graphNetwork.prompts.generators import create_summary_agent_prompt
from graphNetwork.states import OverallState

llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))

def report_writer_node(state: OverallState):
    """
    Generate a final summary report consolidating diagnoses and recommendations.

    This function uses a language model to generate a structured and actionable report
    summarizing the workflow's outcomes. The report is generated based on the state of
    the workflow, which includes data from various agents.

    Args:
        state (OverallState): The current overall state of the workflow.
            - topic (str): The primary topic of analysis.
            - questions (list): Questions addressed during the workflow.
            - analysis (list): Analyses and insights collected from agents.

    Returns:
        dict: A dictionary containing the generated report under the key `final_report`.

    Examples:
        state = OverallState(
            topic="Enhance team collaboration for a multinational company",
            questions=["What are the challenges in team communication?"],
            analysis=["Analysis from agent 1", "Feedback from agent 2"]
             )
            output = report_writer_node(state)
            print(output["final_report"].content)

    """
    print("... Write Report ...")

    # Generate question
    system_message = create_summary_agent_prompt(state)
    report = llm.invoke([SystemMessage(content=system_message)])

    print(f"Report: {report.content}")

    # Write messages to state
    return {"final_report": report}
