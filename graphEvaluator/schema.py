"""
Module defining Pydantic models for structured evaluator output.

This module provides data models for representing evaluation results of reports in a multi-agent system.
Each report is evaluated against criteria, with scores and comments ensuring consistent representation.

Classes:
    Score: Represents the evaluation of a single criterion.
    EvaluatorOutput: Represents the overall evaluation of a single report.
    StructuredEvaluatorOutput: Represents evaluations for all reports in a structured format.
"""

from typing import List
from pydantic import BaseModel, Field

class Score(BaseModel):
    """
    Represents the evaluation of a single criterion for a report.

    Attributes:
        criterion_name (str): The name of the criterion being evaluated.
            Example: "Grammar".
        score (int): The score assigned to this criterion.
            Example: 4.
        comment (str): A comment explaining the score for this criterion.
            Example: "The grammar is perfect."
    """

    criterion_name: str = Field(
        description="The name of the criterion. Example: 'Grammar'",
    )
    score: int = Field(
        description="The score for this criterion. Example: 4",
    )
    comment: str = Field(
        description="A comment about this criterion. Example: 'The grammar is perfect.'",
    )

    @property
    def scores(self) -> str:
        """
        Returns a formatted string representation of the score, including the criterion name, the score, and the comment.

        Returns:
            str: A string summarizing the score.
        """
        return f"Criterion name: {self.criterion_name}\nScore: {self.score}\nComment: {self.comment}\n"


class EvaluatorOutput(BaseModel):
    """
    Represents the overall evaluation of a single report, including scores and an overall comment.

    Attributes:
        anonymized_name (str): An anonymized identifier for the report.
            Example: "Report_1".
        scores (List[Score]): A list of `Score` objects, one for each evaluation criterion.
        overall_comment (str): A summary or explanation of the report's strengths and weaknesses.

            Guidelines:
                - Avoid using names from the `anonymized_name` field (e.g., "Report_1").
                - Use phrases like "this report" to refer to the current report and "other reports"
                  for comparisons.
                - Comments for other reports should be concise and avoid scores.
    """

    anonymized_name: str = Field(
        description="Anonymized name of the report writer. Example: 'Report_1'",
    )

    scores: List[Score] = Field(
        description="A list of dicts with scores for each criterion. Each score contains the criterion name, the score, and a comment."
    )

    overall_comment: str = Field(
        description="A short summary or explanation for this report, highlighting its strengths and weaknesses."
                    "**Don't use names from anonymized_name field, like: 'Report_1', 'first report' and others.**\n"
                    "To express best one use phrase 'this report' and to express other ones use phrase 'other reports'.\n"
                    "Comment for other reports one should be short and without scores."
    )

    @property
    def evaluator_output(self) -> str:
        """
        Returns a formatted string representation of the overall evaluation, including the anonymized name, scores, and overall comment.

        Returns:
            str: A string summarizing the evaluation.
        """
        return f"Anonymized name: {self.nanonymized_nameame}\nScores: {self.scores}\nDescription: {self.description}\n"


class StructuredEvaluatorOutput(BaseModel):
    """
    Represents the evaluations for all reports in a structured format.

    Attributes:
        reports (List[EvaluatorOutput]): A list of `EvaluatorOutput` objects, one for each report.
    """

    reports: List[EvaluatorOutput] = Field(
        description="A list of detailed evaluations for each report."
    )