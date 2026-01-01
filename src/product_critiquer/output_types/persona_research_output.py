from pydantic import BaseModel, Field
from typing import List, Dict, Any


class PersonaResearchOutput(BaseModel):
    """Structured output for persona research task."""

    persona_type: str = Field(..., description="Type of persona researched")
    professional_background: Dict[str, Any] = Field(
        ..., description="Professional context and typical responsibilities"
    )
    technology_profile: Dict[str, Any] = Field(
        ..., description="Technology proficiency, preferences, and usage patterns"
    )
    behavioral_characteristics: Dict[str, Any] = Field(
        ..., description="Behavioral patterns and interaction preferences"
    )
    work_context: Dict[str, Any] = Field(
        ..., description="Work environment, constraints, and pressures"
    )
    pain_points: List[str] = Field(
        ..., description="Common frustrations and challenges with technology"
    )
    decision_factors: List[str] = Field(
        ..., description="Key factors that influence their decision-making"
    )
    research_sources: List[str] = Field(
        ..., description="Sources used for gathering persona information"
    )
    key_insights: List[str] = Field(
        ..., description="Most important insights for user testing simulation"
    )