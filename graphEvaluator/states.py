"""
Module for defining the `OverallState` structure.

The `OverallState` is a `TypedDict` that stores the global state during the evaluation process
in a multi-agent system. It tracks the topic, questionnaire, reports, evaluation results, and the
final selected report.

Dependencies:
    - operator: For merging lists in `evaluator_reports`.
    - typing: For type annotations.

Classes:
    OverallState: Represents the workflow state for evaluation.
"""

import operator
from typing import TypedDict, Annotated, List

from graphEvaluator.schema import EvaluatorOutput


class OverallState(TypedDict):
    """
    Global state for the evaluation workflow.

    Attributes:
        topic (str): Evaluation topic (e.g., "Improving product management maturity").
        questionnaire (str): Questionnaire data used in the evaluation.
        reports (List[dict[str, str, str]]): List of reports to evaluate. Each report includes:
            - `real_name` (str): Original name of the report.
            - `anonymized_name` (str): Anonymized identifier.
            - `report` (str): Report content.
        evaluator_reports (Annotated[List[dict], operator.add]): Results from different evaluators.
        the_best_report_info (str): Final selected report content.
    """

    topic: str
    questionnaire: str
    reports: List[dict[str, str, str]] #
    evaluator_reports: Annotated[List[dict], operator.add]
    the_best_report_info: str