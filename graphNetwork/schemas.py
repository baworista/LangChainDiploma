"""
Class definition for the output structure in agent communication within a multi-agent system.

The `Output` class is a Pydantic model that defines the schema for the messages exchanged
between agents in the workflow. Each instance represents the structured response of an agent,
including the analysis, the assigned task for the next agent, and optional questions.

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
    Represents the output structure for agent communication.

    Attributes:
        name (str): The name of the agent.
        analysis (str): The analysis provided by the agent.
        task (str): The task assigned to the next agent.
        next_agent (Literal): The agent who will handle the next step in the workflow.
        questions (Optional[str]): Questions for the next agent. Defaults to 'NO QUESTIONS' if none provided.
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

