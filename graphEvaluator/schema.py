from pydantic import BaseModel, Field

class EvaluatorOutput(BaseModel):
    anonymized_name: str = Field(
        description="Anonymized name of the report writer. Example: 'Report_1'",
    )
    description: str = Field(
        description="Report's scores and comment",
    )

    @property
    def evaluator_output(self) -> str:
        return f"Anonymized name: {self.nanonymized_nameame}\nDescription: {self.description}\n"
