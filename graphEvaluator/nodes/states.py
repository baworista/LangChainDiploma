import operator
from typing import TypedDict, Annotated, List

from graphEvaluator.schema import EvaluatorOutput


class OverallState(TypedDict):
    topic: str
    questionnaire: str
    reports: List[dict[str, str, str]] #
    evaluator_reports: Annotated[List[dict[str, List[EvaluatorOutput]]], operator.add]
    the_best_report: str