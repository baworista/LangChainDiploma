from pydantic import BaseModel, Field

class EvaluatorOutput(BaseModel):
    anonymized_name: str = Field(
        description="Anonymized name of the report writer. Example: 'Report_1'",
    )
    description: str = Field(
        description="Your output with best report's scores and short comment about other reports."
                    "**Don't use names from anonymized_name field, like: 'Report_1', 'first report' and others.**\n"
                    "To express best one use phrase 'this report' and to express other ones use phrase 'other reports'.\n"
                    "Comment for other reports one should be short and without scores.",
    )

    @property
    def evaluator_output(self) -> str:
        return f"Anonymized name: {self.nanonymized_nameame}\nDescription: {self.description}\n"
