from typing import List

from pydantic import BaseModel, Field


class Agent(BaseModel):
    code_name: str = Field(
        description="Use only provided in system message names"
    )
    name: str = Field(
        description="The human-like name of the analyst persona. "
                    "Ensure the name is realistic and fits the persona."
    )
    role: str = Field(
        description="The specific role of the analyst in the context of the research topic. "
                    "Clearly defines the focus area such as 'Human Resources Analyst' or 'Business Process Analyst'."
    )
    description: str = Field(
        description="A detailed description of the analyst's focus, key competencies, tasks within the project, "
                    "concerns, and motives. This should align with the research topic and the analyst's role."
    )

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nDescription: {self.description}\n"


class Perspectives(BaseModel):
    agents: List[Agent] = Field(
        description="List of agents-analysts where each agents contains name, description and role",
    )


class Response(BaseModel):
    question: str = Field(
        description="Content of agent's current question."
    )

    next_agent: str = Field(
        description="Name of the next node to be called with question."
    )

    current_analysis: str = Field(
        description="Current analysis "
    )
