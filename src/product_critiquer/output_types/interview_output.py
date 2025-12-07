from pydantic import BaseModel, Field
from typing import List, Dict, Any


class InterviewOutput(BaseModel):
    """Structured output for interview simulation task."""

    persona_profile: Dict[str, Any] = Field(
        ..., description="Profile of the persona interviewed"
    )
    interview_questions: List[str] = Field(
        ..., description="Questions asked during interview"
    )
    user_responses: List[str] = Field(..., description="Simulated user responses")
    pain_points_identified: List[str] = Field(
        ..., description="Pain points mentioned in interview"
    )
    satisfaction_score: int = Field(
        ..., ge=1, le=10, description="Overall satisfaction score (1-10)"
    )
    improvement_suggestions: List[str] = Field(
        ..., description="User suggestions for improvement"
    )
    quotes: List[str] = Field(
        default=[], description="Notable user quotes from interview"
    )
