"""
Module defining utility functions and the `OverallState` structure for a multi-agent workflow.

This module includes utility functions for merging strings and deduplicating lists, as well as
a `TypedDict` definition for `OverallState`, which represents the overall state of the workflow.

Functions:
    - merge_str: Ensures that only one topic is retained when merging strings.
    - deduplicate_merge: Merges two lists of strings, removing duplicates.

Class:
    - OverallState: Represents the overall state of the multi-agent workflow, tracking the main task,
      current state, and processed agents.

Functions:
    def merge_str(old_str: str, new_str: str) -> str:
        Ensures that only one topic is retained.

        Args:
            old_str (str): The existing string value.
            new_str (str): The new string value.

        Returns:
            str: The original string (`old_str`) unchanged.

    def deduplicate_merge(old_reviews: List[str], new_reviews: List[str]) -> List[str]:
        Merges two lists of strings, removing duplicates.

        Args:
            old_reviews (List[str]): The existing list of strings.
            new_reviews (List[str]): The new list of strings to merge.

        Returns:
            List[str]: A merged list with duplicates removed.

Class:
    class OverallState(TypedDict):
        Represents the overall state of the workflow.

        Attributes:
            questions (str): Questions for the current workflow step. Defaults to an empty string.
            task (str): The current subtask being addressed. Defaults to an empty string.
            questionnaire (str): The questionnaire data provided for the task.
            good_practices (str): Best practices relevant to the workflow.
            analysis (Annotated[List[str], operator.add]): A list of analyses from agents.
            main_task (str): The overarching goal of the workflow.
            processed_agents (Annotated[List[str], deduplicate_merge]): A deduplicated list of agents
                that have already contributed to the task.
            final_report (str): The final report generated after all agents complete their tasks.
                Defaults to an empty string.

Usage Example:
    state = OverallState(
        questions="What are the key blockers?",
        task="Analyze IT infrastructure.",
        questionnaire="Survey results on IT satisfaction.",
        good_practices="Industry standards for IT management.",
        analysis=["IT analysis: system performance issues"],
        main_task="Optimize organizational IT systems.",
        processed_agents=["IT_Agent"],
        final_report=""
    )
    print(state)

Output:
    {
        "questions": "What are the key blockers?",
        "task": "Analyze IT infrastructure.",
        "questionnaire": "Survey results on IT satisfaction.",
        "good_practices": "Industry standards for IT management.",
        "analysis": ["IT analysis: system performance issues"],
        "main_task": "Optimize organizational IT systems.",
        "processed_agents": ["IT_Agent"],
        "final_report": ""
    }
"""

import operator
from typing import Annotated, TypedDict, List


def merge_str(old_str: str, new_str: str) -> str:
    # Ensure that only one topic is returned
    return old_str


def deduplicate_merge(old_reviews: List[str], new_reviews: List[str]) -> List[str]:
    return list(set(old_reviews).union(new_reviews))


class OverallState(TypedDict):
    questions: str = ""
    task: str = ""
    questionnaire: str
    good_practices: str
    analysis: Annotated[List[str], operator.add]
    main_task: str
    processed_agents: Annotated[List[str], deduplicate_merge]
    final_report: str = ""