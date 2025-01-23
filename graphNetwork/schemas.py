"""
Module: output_structure.

This module defines the `Output` class, a Pydantic model for structuring messages exchanged 
between agents in a multi-agent system. Each instance of the `Output` class represents the 
structured response of an agent, including analysis, tasks, and questions.

Class:
    - Output: Represents the output structure for agent communication.

Attributes:
    name (str): The name of the agent generating the output (e.g., "HR_Agent", "IT_Agent").
    analysis (str): The analysis or insights provided by the agent.
    task (str): The specific task assigned to the next agent, ensuring alignment with their domain.
    next_agent (Literal): The agent responsible for handling the next step in the workflow.
        - Possible values:
            "Consulting_Agent", "HR_Agent", "IT_Agent", "BP_Agent", "KM_Agent", "Summary_Agent".
    questions (Optional[str]): Questions for the next agent to address. Defaults to "NO QUESTIONS" if no questions are provided.

Validation:
    - Ensures the `next_agent` is one of the predefined agents.
    - Provides a default value for `questions` to simplify agent responses.

Usage Example:
    output = Output(
        name="HR_Agent",
        analysis="The current HR practices are inefficient for employee retention.",
        task="Analyze technology solutions to enhance employee engagement.",
        next_agent="IT_Agent",
        questions="What tools are available to automate employee feedback?"
         )
    print(output.dict())
    # Output:
    # {
    #     "name": "HR_Agent",
    #     "analysis": "The current HR practices are inefficient for employee retention.",
    #     "task": "Analyze technology solutions to enhance employee engagement.",
    #     "next_agent": "IT_Agent",
    #     "questions": "What tools are available to automate employee feedback?"
    # }
"""
from typing import Optional, Literal

from pydantic import BaseModel, Field


class Output(BaseModel):
    """
    A Pydantic model representing the output structure for agent communication.

    Attributes:
        name (str): The name of the agent generating the output.
            Example: "HR_Agent".
        analysis (str): The analysis or insights provided by the agent.
            Example: "The current HR practices are inefficient for employee retention."
        task (str): The task assigned to the next agent, ensuring alignment with their domain.
            Example: "Analyze technology solutions to enhance employee engagement."
        next_agent (Literal): The agent responsible for handling the next step in the workflow.
            Allowed values: "Consulting_Agent", "HR_Agent", "IT_Agent", "BP_Agent", "KM_Agent", "Summary_Agent".
            Example: "IT_Agent".
        questions (Optional[str]): Optional questions for the next agent to address.
            Defaults to "NO QUESTIONS" if no questions are provided.
            Example: "What tools are available to automate employee feedback?"
    """

    name: str = Field(description="The name of the agent")
    analysis: str = Field(description="The analysis of the agent")
    task: str = Field(description="The task for the next agent. Must be related to next agent's domain")
    next_agent: Literal[
        "Consulting_Agent", "HR_Agent", "IT_Agent", "BP_Agent", "KM_Agent", "Summary_Agent"
    ] = Field(description="The next agent to handle the message.")
    questions: Optional[str] = Field(
        default="NO QUESTIONS",
        description="Any questions you have for the next agent. Defaults to 'NO QUESTIONS' if none provided."
    )

