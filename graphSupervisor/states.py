"""
Module defining the supervisor state structure for a research workflow.

This module includes definitions for individual research team states, the overall supervisor state,
and utility functions for merging data during the workflow.

Classes:
    - ResearchState: Represents the state of a research team (analyst and reviewer).
    - OverallState: Represents the overall state managed by the supervisor.

Functions:
    - deduplicate_merge: Merges two lists of strings, removing duplicates.

Annotations:
    - Annotated: Used for specifying custom merge or combination behaviors for fields.
"""

import operator
from typing import List, Annotated
from langgraph.graph import MessagesState
from typing_extensions import TypedDict
from graphSupervisor.schema import *


# Individual state for each analyst and reviewer team
class ResearchState(MessagesState):
    """
    Represents the state of a research team, consisting of an analyst and a reviewer.

    Attributes:
        name (str): The name of the research team.
        team_topic (str): The topic assigned to the team.
        description (str): A description of the team's responsibilities and capabilities.
        team_questionnaire (str): The questionnaire results or user input for the team.
        reviews (List[str]): A list of reviews generated by four reviewers.
        analyst (Person): Information about the analyst in the team.
        reviewer (Person): Information about the reviewer in the team.
    """

    name: str
    team_topic: str
    description: str  # Description of team's responsibility and capabilities
    team_questionnaire: str # Questionnaire results or user input
    reviews: Annotated[List[str], operator.add]  # Four reviewers answers
    analyst: Person  # Their info
    reviewer: Person


def deduplicate_merge(old_reviews: List[str], new_reviews: List[str]) -> List[str]:
    """
    Merge two lists of strings, removing duplicates.

    This function is used to combine old and new reviews in a way that ensures no duplicates are present.

    Args:
        old_reviews (List[str]): The existing list of reviews.
        new_reviews (List[str]): The new list of reviews to merge.

    Returns:
        List[str]: A merged list with duplicates removed.
    """
    return list(set(old_reviews).union(new_reviews))

# Overall state for the supervisor
class OverallState(TypedDict):
    """
    Represent the overall state managed by the supervisor.

    Attributes:
        topic (str): The overall topic of analysis.
        questionnaire (str): The questionnaire results or user input for the overall process.
        reviews (List[str]): A deduplicated list of reviews collected from all research teams.
        final_report (str): The final report generated after all analysts complete their tasks.
        teams (List[ResearchTeam]): A list of research teams participating in the workflow.
    """

    topic: str  # Overall topic of analysis
    questionnaire: str  # Questionnaire results or user input
    reviews: Annotated[List[str], deduplicate_merge]  # Four reviewers answers
    final_report: str  # Final report generated after all analysts complete their tasks
    teams: List[ResearchTeam]
