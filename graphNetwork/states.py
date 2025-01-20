import operator
from typing import Annotated, TypedDict, List


def merge_str(old_str: str, new_str: str) -> str:
    # Ensure that only one topic is returned
    return old_str


def deduplicate_merge(old_reviews: List[str], new_reviews: List[str]) -> List[str]:
    return list(set(old_reviews).union(new_reviews))


class OveralState(TypedDict):
    questions: str = ""
    task: str = ""
    questionnaire: str
    good_practices: str
    analysis: Annotated[List[str], operator.add]
    main_task: str
    processed_agents: Annotated[List[str], deduplicate_merge]
    final_report: str = ""