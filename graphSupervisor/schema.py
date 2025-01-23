"""
Module defining data models for research teams and their members using Pydantic.

This module provides structured representations for:
- Persons involved in research teams.
- Research teams with their specific roles and responsibilities.
- Perspectives containing multiple research teams.

Classes:
    - Person: Represents an individual in a research team with detailed attributes.
    - ResearchTeam: Represents a team consisting of an analyst and a reviewer.
    - Perspectives: Represents a collection of research teams.

Attributes in each class are well-defined using Pydantic's `Field` for validation and metadata.
"""

from typing import List
from pydantic import BaseModel, Field


class Person(BaseModel):
    """
    Represent an individual in a research team with attributes defining their role and focus.

    Attributes:
        name (str): The name of the person.
        role (str): The role of the person within the team (e.g., Analyst or Reviewer).
        description (str): A detailed description of the person's key competencies, tasks, concerns, and motives.

    Properties:
        persona (str): A formatted string summarizing the person's details.
    """

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
        """
        Provide a formatted representation of the person's details.

        Returns:
            str: A string containing the name, role, and description of the person.
        """
        return f"Name: {self.name}\nRole: {self.role}\nDescription: {self.description}\n"


class ResearchTeam(BaseModel):
    """
    Represent a research team with a specific focus and roles for its members.

    Attributes:
        name (str): The name of the team (must use predefined names).
        description (str): A brief description of the team's purpose and responsibilities.
        analyst (Person): Information about the analyst in the team.
        reviewer (Person): Information about the reviewer in the team.

    Properties:
        team (str): A formatted string summarizing the team's details, including the analyst and reviewer personas.
    """

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
        Provide a detailed representation of the research team's structure and members.

        Returns:
            str: A string summarizing the team's name, description, and member details.
        """
        return (
            f"Team Name: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"Analyst :\n{self.analyst}\n\n"
            f"Reviewer :\n{self.reviewer}\n"
        )


class Perspectives(BaseModel):
    """
    Represent a collection of research teams.

    Attributes:
        teams (List[ResearchTeam]): A list of research teams, each consisting of a name, description, and assigned analyst and reviewer.
    """

    teams: List[ResearchTeam] = Field(
        description="List of research teams where each team contains name, description and analyst - reviewer duo prompts",
    )