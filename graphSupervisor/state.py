from typing import List, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Analyst(BaseModel):
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
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and description.",
    )


# Overall state for the supervisor
class OverallState(TypedDict):
    topic: str  # Overall topic of analysis
    questionnaire: str  # Questionnaire results or user input
    analysts: List[Analyst] # All analysts
    analyst_progress: Dict[str, bool]  # Progress of each analyst (e.g., {'HRAnalyst': True})
    aggregated_diagnosis: List[str]  # Combined diagnosis from all analysts
    aggregated_recommendations: List[str]  # Combined recommendations from all analysts
    final_report: str  # Final report generated after all analysts complete their tasks


# Individual state for each analyst
class AnalystState(TypedDict):
    analyst_name: str  # Name of the analyst (e.g., HRAnalyst, BPAnalyst)
    topic: str  # Topic assigned to the analyst
    goals: str  # Goals or focus of this analyst (e.g., HR-specific goals)
    diagnosis: List[str]  # Analyst-specific diagnosis
    recommendations: List[str]  # Analyst-specific recommendations
