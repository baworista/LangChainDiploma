"""
Module for selecting the best report in a multi-agent system.

This module defines the `final_evaluator_node` function, which uses a language model to analyze
reports, feedback, and context to identify the best submission and justify the choice.

Functionality:
    - Analyzes topic, questionnaire, reports, and evaluator feedback.
    - Selects the best report based on evaluation criteria (e.g., relevance, clarity).
    - Outputs the selected report and justification for its choice.

Dependencies:
    - `langchain_core.messages`: For generating system prompts.
    - `langchain_openai`: For querying OpenAI's language model.
    - `graphEvaluator.states`: Provides the `OverallState` definition.

Function:
    - `final_evaluator_node`: Evaluates and selects the best report.

Example:
    state = {
        "topic": "Improve team collaboration.",
        "questionnaire": "Survey on team dynamics.",
        "reports": {
            "Report_1": "Analysis of team performance.",
            "Report_2": "Collaboration improvement strategies."
        },
        "evaluator_reports": [
            {"Report_1": {"clarity": 4, "actionability": 3}},
            {"Report_2": {"clarity": 5, "actionability": 4}}
        ]
    }

    output = final_evaluator_node(state)
    print(output["the_best_report_info"])
"""

import os

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from graphEvaluator.states import OverallState


llm = ChatOpenAI(model_name=os.getenv("MODEL_SUPERVISOR"))

eval_prompt="""
You are the final evaluator in a multi-agent system tasked with selecting the best report. Your role is to carefully analyze and compare all the provided materials, including:

Main Topic: The central theme or subject matter of the evaluation.
{topic}
Questionnaire: A set of questions used to assess the reports.
{questionnaire}
Reports: The submissions prepared by agents addressing the main topic and questionnaire.
{reports}
Evaluator Reports: Feedback or assessments from other evaluators regarding the reports.
{evaluator_reports}

Your Objective: Based on provided information, select the best report. Provide a justification for your decision, clearly explaining why the chosen report excels in meeting the evaluation criteria.
Note: you have information about anonymized and real names of reports, in your final output use the 'anonymized-real name' mapping, like 'Report_1-Supervisor'.
"""


def final_evaluator_node(state: OverallState):
    """
    Select the best report from the provided submissions and justifies the choice.

    Args:
        state (OverallState): The current state of the workflow, containing:
            - topic (str): The main topic of the evaluation.
            - questionnaire (str): Questionnaire used for report evaluation.
            - reports (dict): Reports submitted by agents.
            - evaluator_reports (list): Feedback from other evaluators.

    Returns:
        dict: A dictionary with the key `the_best_report_info`, containing the best report
        and the justification for its selection.

    Example:
        state = {
            "topic": "Optimize collaboration.",
            "questionnaire": "Survey data.",
            "reports": {
                "Report_1": "Detailed analysis.",
                "Report_2": "Strategies for improvement."
            },
            "evaluator_reports": [
                {"Report_1": {"clarity": 4, "actionability": 3}},
                {"Report_2": {"clarity": 5, "actionability": 4}}
            ]
        }

        output = final_evaluator_node(state)
        print(output["the_best_report_info"])
    """
    print("Final Evaluator activated.")

    topic = state["topic"]
    questionnaire = state["questionnaire"]
    reports = state["reports"]
    evaluator_reports = state["evaluator_reports"]

    prompt = eval_prompt.format(topic=topic,
                                questionnaire=questionnaire,
                                reports=reports,
                                evaluator_reports=evaluator_reports)

    prompt = [SystemMessage(content=prompt)]


    output = llm.invoke(prompt)

    return {"the_best_report_info": output}