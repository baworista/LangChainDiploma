import operator
from typing import TypedDict, Annotated, List


class OverallState(TypedDict):
    topic: str
    questionnaire: str
    reports: List[dict]
    evaluator_reports: Annotated[List[dict[str, str]], operator.add]
    the_best_report: str