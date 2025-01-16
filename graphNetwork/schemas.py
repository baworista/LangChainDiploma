from typing import Optional, Literal

from pydantic import BaseModel, Field


class Output(BaseModel):
    """
    Represents the output structure for agent communication.

    Attributes:
        name (str): The name of the agent.
        analysis (str): The analysis provided by the agent.
        task (str): The task assigned to the next agent.
        next_agent (Agent): The agent who will handle the next step.
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

