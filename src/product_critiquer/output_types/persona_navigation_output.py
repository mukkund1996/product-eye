from pydantic import BaseModel, Field
from typing import List, Dict, Any


class PersonaNavigationOutput(BaseModel):
    """Structured output for persona navigation task."""

    url_tested: str = Field(..., description="URL that was tested")
    persona_type: str = Field(..., description="Type of persona used for testing")
    navigation_path: List[str] = Field(
        ..., description="Sequence of pages/actions taken"
    )
    interactions: List[Dict[str, Any]] = Field(
        ..., description="Detailed interaction data"
    )
    observations_made: List[str] = Field(
        default=[], description="Key observations and interface notes"
    )
    issues_found: List[Dict[str, Any]] = Field(
        default=[], description="Issues or pain points discovered"
    )
    completion_status: str = Field(
        ..., description="Whether task was completed successfully"
    )
    performance_metrics: Dict[str, Any] = Field(
        default={}, description="Performance data collected"
    )
