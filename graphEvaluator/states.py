"""
Module defining the `OverallState` structure for managing the workflow state in a multi-agent system.

The `OverallState` is a `TypedDict` that represents the global state during the evaluation process. It includes
information about the evaluation topic, questionnaire, reports, evaluator results, and the final selected report.

Classes:
    - OverallState: A dictionary-based structure to store and manage the evaluation workflow's global state.

Dependencies:
    - operator: For managing list merging operations with `operator.add`.
    - typing: For type annotations, including `TypedDict` and `Annotated`.
    - graphEvaluator.schema.EvaluatorOutput: Defines the structure for individual evaluator outputs.

Class: OverallState
    Represents the global state in the evaluation workflow.

    Attributes:
        topic (str): The main topic or subject being evaluated.
            Example: "Improving product management maturity for multinational companies."
        questionnaire (str): The questionnaire data used to guide the evaluation process.
            Example: "Survey questions and responses from key stakeholders."
        reports (List[dict[str, str, str]]): A list of dictionaries containing the reports to be evaluated.
            Each dictionary includes:
                - `real_name` (str): The original name of the report source.
                - `anonymized_name` (str): An anonymized identifier for the report.
                - `report` (str): The content of the report.
        evaluator_reports (Annotated[List[dict], operator.add]): A list of evaluation results generated
            by different evaluators. New evaluations are added to the list during the workflow.
        the_best_report_info (str): The final selected report's content, determined after all evaluations.

Example Usage:
    # Define a sample state
    state = OverallState(
        topic="Improving product management maturity",
        questionnaire="Survey responses regarding current practices.",
        reports=[
            {"real_name": "Supervisor", "anonymized_name": "Report_1", "report": "Content for Supervisor report."},
            {"real_name": "Network", "anonymized_name": "Report_2", "report": "Content for Network report."},
        ],
        evaluator_reports=[
            {"anonymized_name": "Report_1", "scores": [...], "overall_comment": "Strong in clarity."},
            {"anonymized_name": "Report_2", "scores": [...], "overall_comment": "Weak in relevance."},
        ],
        the_best_report_info="Report_1 is the best report due to its comprehensive analysis and clarity."
    )

    # Access the best report
    print(state["the_best_report_info"])

Output:
    Report_1 is the best report due to its comprehensive analysis and clarity.
"""

import operator
from typing import TypedDict, Annotated, List

from graphEvaluator.schema import EvaluatorOutput


class OverallState(TypedDict):
    topic: str
    questionnaire: str
    reports: List[dict[str, str, str]] #
    evaluator_reports: Annotated[List[dict], operator.add]
    the_best_report_info: str