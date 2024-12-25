import operator
from typing import List, Annotated

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class ResearchTeam(BaseModel):
    name: str = Field(
        description="Use only provided in system message names"
    )

    description: str = Field(
        description="Short description of what this team is response for."
    )

    analyst_prompt: str = Field(
        description="The specific prompt for the analyst in the context of the research topic. "
                    "Clearly defines the focus area such as 'Human Resources' or 'Business Process'. "
                    "\n +"
                    "A description of the analyst's focus, key competencies, tasks within the project, "
                    "concerns, and motives. This should align with the research topic and the analyst's role."
    )

    reviewer_prompt: str = Field(
        description="The specific prompt for the reviewer in the context of the research topic. "
                    "Clearly defines the focus area such as 'Human Resources' or 'Business Process'. "
                    "\n +"
                    "A description of the reviewer's focus, key competencies, tasks within the project, "
                    "concerns, and motives. This should align with the research topic and the reviewer's role."
    )

    @property
    def experts(self) -> str:
        """
        Provides a detailed representation of the research team's persona,
        including its name, description, and the specific prompts for the analyst and reviewer.
        """
        return (
            f"Team Name: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"Analyst Prompt:\n{self.analyst_prompt}\n\n"
            f"Reviewer Prompt:\n{self.reviewer_prompt}\n"
        )


class Perspectives(BaseModel):
    teams: List[ResearchTeam] = Field(
        description="List of research teams where each team contains name, description and analyst - reviewer duo prompts",
    )


# Individual state for each analyst and reviewer team
class ResearchState(MessagesState):
    name: str
    team_topic: str
    description: str  # Description of team's responsibility and capabilities
    team_questionnaire: str # Questionnaire results or user input
    reviews: Annotated[List[str], operator.add]  # Four reviewers answers
    analyst_prompt: str  # Their info
    reviewer_prompt: str


def deduplicate_merge(old_reviews: List[str], new_reviews: List[str]) -> List[str]:
    return list(set(old_reviews).union(new_reviews))

# Overall state for the supervisor
class OverallState(TypedDict):
    topic: str  # Overall topic of analysis
    questionnaire: str  # Questionnaire results or user input
    reviews: Annotated[List[str], deduplicate_merge]  # Four reviewers answers
    final_report: str  # Final report generated after all analysts complete their tasks
    teams: List[ResearchTeam]
