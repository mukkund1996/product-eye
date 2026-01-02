from pydantic import BaseModel, Field
from typing import List, Dict, Any


class TestingInstructionResult(BaseModel):
    """Result for individual testing instruction execution"""

    task_description: str = Field(
        ..., description="The testing instruction task description"
    )
    priority: str = Field(..., description="Priority level of the task")
    max_attempts: int = Field(..., description="Maximum allowed attempts")
    attempts_made: int = Field(..., description="Number of attempts actually made")
    success_criteria: str = Field(..., description="Success criteria for the task")
    success_criteria_met: bool = Field(
        ..., description="Whether success criteria were met"
    )
    fallback_action: str = Field(
        ..., description="Fallback action if task cannot be completed"
    )
    fallback_executed: bool = Field(
        default=False, description="Whether fallback action was executed"
    )
    completion_notes: str = Field(
        ..., description="Detailed notes about task execution"
    )
    final_status: str = Field(..., description="Final status: completed/failed/partial")


class PersonaNavigationOutput(BaseModel):
    """Structured output for persona navigation task."""

    url_tested: str = Field(..., description="URL that was tested")
    persona_type: str = Field(..., description="Type of persona used for testing")

    testing_instruction_results: List[TestingInstructionResult] = Field(
        ..., description="Detailed results for each testing instruction"
    )

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

    overall_completion_status: str = Field(
        ..., description="Overall completion status across all testing instructions"
    )
    high_priority_tasks_completed: int = Field(
        default=0, description="Number of high priority tasks completed successfully"
    )
    total_high_priority_tasks: int = Field(
        default=0, description="Total number of high priority tasks"
    )

    performance_metrics: Dict[str, Any] = Field(
        default={}, description="Performance data collected"
    )
