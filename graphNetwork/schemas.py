from pydantic import BaseModel, Field


class Agent(BaseModel):
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
