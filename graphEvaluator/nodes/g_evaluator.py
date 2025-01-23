"""
Module for evaluating reports using the G-Eval framework.

Defines the `g_eval_evaluator_node` function, which evaluates reports based on multiple criteria
(relevance, factuality, completeness, clarity, and actionability) using the G-Eval metric.

Functionality:
    - Processes anonymized reports.
    - Evaluates each report based on predefined criteria.
    - Returns detailed scores and comments for each criterion.

Dependencies:
    - `dotenv`: Loads environment variables.
    - `graphEvaluator.states`: Provides the `OverallState` structure.
    - `deepeval`: Supplies G-Eval metrics and test cases.

Function:
    - `g_eval_evaluator_node`: Main function for evaluating reports.
"""

from dotenv import load_dotenv
from graphEvaluator.states import OverallState

# Install DeepEval library
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

load_dotenv()

def g_eval_evaluator_node(state: OverallState):
    """
    Evaluate reports using G-Eval metrics and generates detailed feedback.

    Args:
        state (OverallState): Current workflow state containing:
            - reports (dict): Dictionary of reports with:
                - anonymized_name (str): The anonymized report name.
                - report (str): Content of the report.

    Returns:
        dict: Results of G-Eval evaluation under the `evaluator_reports` key.

    Example:
        state = {
            "reports": {
                "Report_1": {"anonymized_name": "Anonymized_1", "report": "Content 1"},
                "Report_2": {"anonymized_name": "Anonymized_2", "report": "Content 2"}
            }
        }

        output = g_eval_evaluator_node(state)
        print(output["evaluator_reports"])
    """
    print("G-Eval Evaluator activated.")

    reports = state["reports"]
    criteria = [
        {
            "name": "Relevance",
            "criteria": "Relevance - How well does the report address the task?"
        },
        {
            "name": "Factuality",
            "criteria": "Factuality - Does the report contain any factual errors?"
        },
        {
            "name": "Completeness",
            "criteria": "Completeness - Does the report fully cover all aspects of the task (diagnosis and recommendations)?"
        },
        {
            "name": "Clarity",
            "criteria": "Clarity - Is the report well-structured and easy to understand?"
        },
        {
            "name": "Actionability",
            "criteria": "Actionability - Are the recommendations practical and applicable?"
        }
    ]

    results = []

    anonymized_reports = {
        report_data["anonymized_name"]: report_data["report"]
        for real_name, report_data in reports.items()
    }

    # Evaluate each report using G-Eval
    for anonymized_name, report_content in anonymized_reports.items():
        print(f"Evaluating report: {anonymized_name}")

        report_results = []

        for criterion in criteria:
            test_case = LLMTestCase(
                input="Evaluation based on criterion: " + criterion["criteria"],
                actual_output=report_content
            )

            metric = GEval(
                name=criterion["name"],
                criteria=criterion["criteria"],
                evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
            )

            metric.measure(test_case)

            report_results.append({
                "criterion_name": criterion["name"],
                "score": metric.score,
                "comment": metric.reason
            })

        results.append({
            "anonymized_name": anonymized_name,
            "scores": report_results
        })

    # Construct the final output
    detailed_result = {"g-evaluator": results}

    return {"evaluator_reports": [detailed_result]}
