import operator
from typing import Annotated, TypedDict, List


class OveralState(TypedDict):
    questions: str = ""
    task: str = ""
    questionare: str
    good_practices: str
    analysis: Annotated[List[str], operator.add]
    main_task: str
    processed_agents: Annotated[List[str], operator.add]
    final_report: str = ""