from typing import List
from pydantic import BaseModel, Field

class Score(BaseModel):
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
        return f"Criterion name: {self.criterion_name}\nScore: {self.score}\nComment: {self.comment}\n"


class EvaluatorOutput(BaseModel):
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
        return f"Anonymized name: {self.nanonymized_nameame}\nScores: {self.scores}\nDescription: {self.description}\n"


class StructuredEvaluatorOutput(BaseModel):
    reports: List[EvaluatorOutput] = Field(
        description="A list of detailed evaluations for each report."
    )