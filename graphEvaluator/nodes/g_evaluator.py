"""
Module for evaluating reports using the G-Eval framework in a multi-agent system.

This module defines the `g_eval_evaluator_node` function, which uses the DeepEval library's G-Eval metric
to assess anonymized reports based on predefined evaluation criteria. The results include scores and
justifications for each criterion.

Functionality:
    - Evaluates reports on the following criteria:
        1. Relevance: How well the report addresses the task.
        2. Factuality: Whether the report contains factual errors.
        3. Completeness: Whether the report fully covers all aspects of the task (diagnosis and recommendations).
        4. Clarity: Whether the report is well-structured and easy to understand.
        5. Actionability: Whether the recommendations are practical and applicable.
    - Uses anonymized report names to ensure unbiased evaluation.
    - Outputs detailed scores and comments for each criterion.

Dependencies:
    - dotenv: For loading environment variables.
    - graphEvaluator.states: Contains the `OverallState` class for managing the workflow state.
    - deepeval.test_case: Provides the `LLMTestCase` and `LLMTestCaseParams` classes for evaluation.
    - deepeval.metrics: Provides the `GEval` metric for scoring reports.

Functions:
    - g_eval_evaluator_node: Evaluates reports based on G-Eval criteria and returns detailed results.

Classes and Methods:
    - LLMTestCase: Represents a test case for evaluating a report.
    - GEval: Metric for assessing reports based on specific criteria.

Example Usage:
    state = {
        "reports": {
            "Report_1": {
                "anonymized_name": "Anonymized_1",
                "report": "Detailed analysis on task performance."
            },
            "Report_2": {
                "anonymized_name": "Anonymized_2",
                "report": "Recommendations for improving operations."
            }
        }
    }

    output = g_eval_evaluator_node(state)
    print(output["evaluator_reports"])

Output:
    {
        "evaluator_reports": [
            {
                "g-evaluator": [
                    {
                        "anonymized_name": "Anonymized_1",
                        "scores": [
                            {"criterion_name": "Relevance", "score": 4.5, "comment": "Addresses the task effectively."},
                            {"criterion_name": "Factuality", "score": 5, "comment": "No factual errors found."},
                            ...
                        ]
                    },
                    {
                        "anonymized_name": "Anonymized_2",
                        "scores": [
                            {"criterion_name": "Relevance", "score": 4, "comment": "Covers most aspects of the task."},
                            ...
                        ]
                    }
                ]
            }
        ]
    }
"""
from dotenv import load_dotenv
from graphEvaluator.states import OverallState

# Install DeepEval library
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

load_dotenv()

def g_eval_evaluator_node(state: OverallState):
    """
    Evaluates anonymized reports using G-Eval criteria and generates a detailed evaluation report.

    Args:
        state (OverallState): The current state of the workflow, which includes:
            - "reports" (dict): A dictionary of reports, where each report contains:
                - "anonymized_name" (str): The anonymized name of the report.
                - "report" (str): The content of the report.

    Returns:
        dict: A dictionary containing G-Eval evaluation results under the key `evaluator_reports`.

    Evaluation Criteria:
        - Relevance: How well the report addresses the task.
        - Factuality: Whether the report contains factual errors.
        - Completeness: Whether the report fully covers all aspects of the task.
        - Clarity: Whether the report is well-structured and easy to understand.
        - Actionability: Whether the recommendations are practical and applicable.

    Example:
        state = {
            "reports": {
                "Report_1": {
                    "anonymized_name": "Anonymized_1",
                    "report": "Detailed analysis on task performance."
                },
                "Report_2": {
                    "anonymized_name": "Anonymized_2",
                    "report": "Recommendations for improving operations."
                }
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
