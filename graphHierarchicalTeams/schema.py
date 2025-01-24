"""
Module defining data models for hierarchical teams using Pydantic.

This module provides structured representations for persons, subordinate teams,
research teams, and their hierarchical relationships. It uses Pydantic to enforce
validation and provides helper methods to present detailed representations of the entities.

Classes:
    - Person: Represents an individual with a name, role, and description.
    - SubordinateTeam: Represents a subordinate team with its name, description, and supervisor.
    - ResearchTeam: Represents a research team with its name, description, and analyst-reviewer duo.
    - Subordinates: A container for multiple subordinate teams.
    - Perspectives: A container for multiple research teams.
"""

from typing import List
from pydantic import BaseModel, Field


class Person(BaseModel):
    """Represent a person involved in a team with specific responsibilities."""

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
        """Provide a formatted representation of the person's details."""
        return f"Name: {self.name}\nRole: {self.role}\nDescription: {self.description}\n"


class SubordinateTeam(BaseModel):
    """Represent a subordinate team in the hierarchical structure."""

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
        """Provide a detailed representation of the subordinate team."""
        return (
            f"Subordinate Team Name: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"Subordinate :\n{self.subordinate}\n\n"
        )


class ResearchTeam(BaseModel):
    """Represent a research team with an analyst and a reviewer."""

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
        """Provide a detailed representation of the research team."""
        return (
            f"Team Name: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"Analyst :\n{self.analyst}\n\n"
            f"Reviewer :\n{self.reviewer}\n"
        )


class Subordinates(BaseModel):
    """Represent a container for multiple subordinate teams."""

    subordinates: List[SubordinateTeam] = Field(
        description="List of subordinate teams with supervisor's name, role, and description.",
    )


class Perspectives(BaseModel):
    """Represent a container for multiple research teams."""

    teams: List[ResearchTeam] = Field(
        description="List of research teams where each team contains name, description and analyst - reviewer duo prompts",
    )