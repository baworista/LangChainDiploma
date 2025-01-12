import operator
from typing import Annotated, List, TypedDict

from langgraph.graph import MessagesState

from graphHierarchicalTeams.schema import Person, ResearchTeam


# Individual state for each analyst and reviewer team
class ResearchState(MessagesState):
    name: str
    team_topic: str
    description: str  # Description of team's responsibility and capabilities
    team_questionnaire: str # Questionnaire results or user input
    reviews: Annotated[List[str], operator.add]  # Four reviewers answers
    analyst: Person  # Their info
    reviewer: Person


def deduplicate_merge(old_reviews: List[str], new_reviews: List[str]) -> List[str]:
    return list(set(old_reviews).union(new_reviews))


class subordinate_team(TypedDict):
    name: str
    subordinate: Person
    teams: List[ResearchTeam]
    team_reviews: Annotated[List[str], deduplicate_merge]  # Four teams analysis


# Overall state for the supervisor
class OverallState(TypedDict):
    topic: str  # Overall topic of analysis
    questionnaire: str  # Questionnaire results or user input

    subordinate_reviews: Annotated[List[str], deduplicate_merge]  # Two subordinate supervisors answers
    final_report: str  # Final report generated after all analysts complete their tasks

    subordinates: List[Person]  # List of subordinate supervisors