"""
Module for evaluating individual reports in a multi-agent system.

This module defines functions to evaluate individual reports based on predefined criteria.
Each report is assessed in isolation to ensure objective evaluation without influence from
other reports. The results include detailed scores and comments for each criterion, as well
as an overall comment summarizing the evaluation.

Evaluation Criteria:
1. **Relevance**: How well the report addresses the task.
2. **Factuality**: Whether the report contains any factual errors.
3. **Completeness**: Whether the report fully covers all aspects of the task (diagnosis and recommendations).
4. **Clarity**: Whether the report is well-structured and easy to understand.
5. **Actionability**: Whether the recommendations are practical and applicable.

Dependencies:
    - langchain_core.messages: For creating system messages for the language model.
    - langchain_openai: For interacting with OpenAI's language model.
    - graphEvaluator.states: Defines the `OverallState` class for managing workflow state.
    - graphEvaluator.schema: Defines the `EvaluatorOutput` schema for structured evaluations.

Functions:
    - evaluate_single_report: Evaluates a single report using an LLM and returns structured output.
    - individual_evaluator_node: Processes all reports in the state and returns evaluation results.

Prompt Structure:
    - Topic: The main topic of the report.
    - Questionnaire: Questions used to guide the report's preparation.
    - Report: The specific report being evaluated.
    - Criteria: Detailed instructions for scoring and justifying the evaluation.

Example Usage:
    state = {
        "topic": "Optimize team collaboration in multinational organizations.",
        "questionnaire": "Survey data on team communication barriers.",
        "reports": {
            "Report_1": {
                "anonymized_name": "Anonymized_1",
                "report": "Detailed analysis of team dynamics."
            },
            "Report_2": {
                "anonymized_name": "Anonymized_2",
                "report": "Recommendations for improving team collaboration."
            }
        }
    }

    output = individual_evaluator_node(state)
    print(output["evaluator_reports"])

Output:
    {
        "evaluator_reports": [
            {
                "individual_evaluator": [
                    {
                        "anonymized_name": "Anonymized_1",
                        "scores": {
                            "Relevance": 4,
                            "Factuality": 5,
                            "Completeness": 3,
                            "Clarity": 4,
                            "Actionability": 3
                        },
                        "overall_comment": "Addresses team dynamics effectively but lacks actionable recommendations."
                    },
                    ...
                ]
            }
        ]
    }
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
    Evaluates a single report using an LLM and returns a structured output.

    Args:
        report (str): The content of the report to evaluate.
        topic (str): The main topic of the evaluation.
        questionnaire (str): The questionnaire data used for the report.

    Returns:
        EvaluatorOutput: A structured evaluation result, including scores and comments.
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
    Processes all reports in the state, evaluates them individually, and returns the results.

    Args:
        state (OverallState): The current workflow state, including:
            - "topic" (str): The main topic of the evaluation.
            - "questionnaire" (str): The questionnaire used for the reports.
            - "reports" (dict): A dictionary of reports with anonymized names and content.

    Returns:
        dict: A dictionary containing the evaluation results for all reports under the key `evaluator_reports`.

    Example:
        state = {
            "topic": "Optimize team collaboration in multinational organizations.",
            "questionnaire": "Survey data on team communication barriers.",
            "reports": {
                "Report_1": {
                    "anonymized_name": "Anonymized_1",
                    "report": "Detailed analysis of team dynamics."
                },
                "Report_2": {
                    "anonymized_name": "Anonymized_2",
                    "report": "Recommendations for improving team collaboration."
                }
            }
        }

        output = individual_evaluator_node(state)
        print(output["evaluator_reports"])
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