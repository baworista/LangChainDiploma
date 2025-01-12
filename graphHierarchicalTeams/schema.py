from typing import List
from pydantic import BaseModel, Field


class Person(BaseModel):
    name: str = Field(
        description="Human-like person's name"
    )
    role: str = Field(
        description="Role of the person in the team and in context of the topic.",
    )
    description: str = Field(
        description="Description of the person's focus, key competencies, tasks in the project and concerns, and motives.",
    )

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nDescription: {self.description}\n"


class SubordinateTeam(BaseModel):
    name: str = Field(
        description="Use only provided in system message names"
    )

    description: str = Field(
        description="Short description of what this team is response for."
    )

    subordinate: Person = Field(
        description="Subordinate supervisor person"
    )

    @property
    def team(self) -> str:
        """
        Provides a detailed representation of the team
        """
        return (
            f"Subordinate Team Name: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"Subordinate :\n{self.subordinate}\n\n"
        )


class ResearchTeam(BaseModel):
    name: str = Field(
        description="Use only provided in system message names"
    )

    description: str = Field(
        description="Short description of what this team is response for."
    )

    analyst: Person = Field(
        description="Analyst person"
    )

    reviewer: Person = Field(
        description="Reviewer person"
    )

    @property
    def team(self) -> str:
        """
        Provides a detailed representation of the research team's persona,
        including its name, description, and the specific prompts for the analyst and reviewer.
        """
        return (
            f"Team Name: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"Analyst :\n{self.analyst}\n\n"
            f"Reviewer :\n{self.reviewer}\n"
        )


class Subordinates(BaseModel):
    subordinates: List[SubordinateTeam] = Field(
        description="List of subordinate teams with supervisor's name, role, and description.",
    )


class Perspectives(BaseModel):
    teams: List[ResearchTeam] = Field(
        description="List of research teams where each team contains name, description and analyst - reviewer duo prompts",
    )