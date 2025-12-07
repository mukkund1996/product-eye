from pydantic import BaseModel, Field
from typing import List, Dict, Any


class FinalReportOutput(BaseModel):
    """Structured output for final report task."""

    executive_summary: str = Field(..., description="High-level summary of findings")
    tested_scenarios: List[str] = Field(..., description="Scenarios that were tested")
    persona_insights: Dict[str, Any] = Field(
        ..., description="Insights from different persona types"
    )
    critical_issues: List[Dict[str, Any]] = Field(
        ..., description="Most important issues found"
    )
    usability_score: float = Field(
        ..., ge=0, le=10, description="Overall usability score"
    )
    recommendations: List[Dict[str, Any]] = Field(
        ..., description="Prioritized recommendations"
    )
    metrics_summary: Dict[str, Any] = Field(
        default={}, description="Performance and usage metrics"
    )
