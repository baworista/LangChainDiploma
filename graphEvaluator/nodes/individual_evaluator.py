"""
Module for evaluating individual reports in a multi-agent system.

This module defines functions to evaluate reports in isolation based on predefined criteria.
Each report is assessed independently to ensure objective and unbiased results.
The evaluation includes detailed scores and comments for each criterion, along with
an overall summary.

Functionality:
    - Evaluates reports on the following criteria:
        1. Relevance: How well the report addresses the task.
        2. Factuality: Whether the report contains any factual errors.
        3. Completeness: Coverage of all task aspects (diagnosis and recommendations).
        4. Clarity: Whether the report is well-structured and easy to understand.
        5. Actionability: Practicality and applicability of the recommendations.
    - Processes all reports in the workflow state individually.
    - Outputs structured results for each report.

Dependencies:
    - `langchain_core.messages`: For generating system prompts.
    - `langchain_openai`: For querying the OpenAI language model.
    - `graphEvaluator.states`: Defines the `OverallState` structure.
    - `graphEvaluator.schema`: Provides the `EvaluatorOutput` structure.

Functions:
    - `evaluate_single_report`: Evaluates a single report and returns structured feedback.
    - `individual_evaluator_node`: Processes all reports in the state and compiles evaluation results.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from graphEvaluator.states import OverallState
from graphEvaluator.schema import EvaluatorOutput

load_dotenv()
llm = ChatOpenAI(model_name=os.getenv("MODEL_SUPERVISOR"))

evaluator_prompt = """
    Task: You are an individual evaluator reviewing a single report compiled by an anonymous team on topic: {topic}.
    You are aware that there are multiple reports, but you will evaluate only this one in isolation.
    With asked questions and answers on it: {questionnaire}

    Report: {report}

    Evaluate the report based on the following criteria:
    1. Relevance: How well does the report address the task?
    2. Factuality: Does the report contain any factual errors?
    3. Completeness: Does the report fully cover all aspects of the task (diagnosis and recommendations)?
    4. Clarity: Is the report well-structured and easy to understand?
    5. Actionability: Are the recommendations practical and applicable?

    **Provide a score (1-5) for each criterion and include a detailed and specific explanation for the report.**
    **Ensure that your evaluation is critical and fair: Avoid giving the highest scores (5) unless the report clearly demonstrates exceptional quality in that criterion.**
    **Justify your evaluation and highlight key strengths and weaknesses of the report.**
"""


def evaluate_single_report(report: str, topic: str, questionnaire: str) -> EvaluatorOutput:
    """
    Evaluate a single report in isolation using an LLM.

    Args:
        report (str): The content of the report to evaluate.
        topic (str): The main topic of the evaluation.
        questionnaire (str): The questionnaire data used for the report.

    Returns:
        EvaluatorOutput: Structured evaluation results with scores and comments.
    """
    system_prompt = evaluator_prompt.format(
        topic=topic,
        questionnaire=questionnaire,
        report=report
    )

    structured_llm = llm.with_structured_output(EvaluatorOutput)
    system_message = SystemMessage(content=system_prompt)

    # Query the LLM and get the structured output
    return structured_llm.invoke([system_message])


def individual_evaluator_node(state: OverallState):
    """
    Process and evaluates all reports individually, returning structured results.

    Args:
        state (OverallState): Current workflow state, including:
            - topic (str): The evaluation topic.
            - questionnaire (str): Questions guiding the reports.
            - reports (dict): Dictionary of anonymized reports with their content.

    Returns:
        dict: Structured evaluation results under the `evaluator_reports` key.
    """
    print("Individual Evaluator activated.")

    reports = state["reports"]
    topic = state["topic"]
    questionnaire = state["questionnaire"]

    results = []

    anonymized_reports = {
        report_data["anonymized_name"]: report_data["report"]
        for real_name, report_data in reports.items()
    }

    # Evaluate each report using G-Eval
    for anonymized_name, report_content in anonymized_reports.items():
        print(f"Evaluating report: {anonymized_name}")

        # Evaluate the report in isolation
        evaluation_result = evaluate_single_report(
            report=report_content,
            topic=topic,
            questionnaire=questionnaire
        )

        # Append the structured evaluation to results
        results.append({
            "anonymized_name": anonymized_name,
            "scores": evaluation_result.scores,
            "overall_comment": evaluation_result.overall_comment
        })

    # Construct the final output
    detailed_result = {"individual_evaluator": results}

    return {"evaluator_reports": [detailed_result]}