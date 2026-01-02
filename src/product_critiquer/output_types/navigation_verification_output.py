from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
from enum import Enum


class VerificationDecision(str, Enum):
    """Possible decisions from navigation verification"""
    PROCEED = "PROCEED"
    RETRY = "RETRY"
    ACCEPTABLE_WITH_MAX_ATTEMPTS = "ACCEPTABLE_WITH_MAX_ATTEMPTS"


class TaskVerificationResult(BaseModel):
    """Verification result for individual testing instruction task"""
    task_description: str = Field(..., description="The task that was being verified")
    priority: str = Field(..., description="Priority level of the task")
    max_attempts: int = Field(..., description="Maximum allowed attempts for this task")
    attempts_made: int = Field(..., description="Number of attempts actually made")
    completion_status: str = Field(..., description="Whether task was completed successfully")
    success_criteria_met: bool = Field(..., description="Whether success criteria were satisfied")
    verification_notes: str = Field(..., description="Detailed notes about task completion quality")
    needs_retry: bool = Field(..., description="Whether this task should be retried")
    can_retry: bool = Field(..., description="Whether retry is possible (within max_attempts)")


class NavigationVerificationOutput(BaseModel):
    """Structured output for navigation verification task."""

    persona_type: str = Field(..., description="Type of persona that was tested")
    url_tested: str = Field(..., description="URL that was tested")
    overall_assessment: Literal["satisfactory", "needs_improvement", "acceptable_with_max_attempts"] = Field(
        ..., description="Overall quality assessment of navigation completion"
    )
    
    task_verifications: List[TaskVerificationResult] = Field(
        ..., description="Verification results for each testing instruction task"
    )
    
    completion_rate: float = Field(
        ..., description="Percentage of tasks completed successfully"
    )
    
    priority_tasks_completed: Dict[str, int] = Field(
        default={}, description="Count of completed tasks by priority level"
    )
    
    feedback_summary: List[str] = Field(
        default=[], description="Key feedback points for improvement"
    )
    
    missing_requirements: List[str] = Field(
        default=[], description="Important requirements that were not met"
    )
    
    final_decision: VerificationDecision = Field(
        ..., description="Final decision: PROCEED, RETRY, or ACCEPTABLE_WITH_MAX_ATTEMPTS"
    )
    
    retry_guidance: str = Field(
        default="", description="Specific guidance for retry attempts if needed"
    )
    
    verification_notes: str = Field(
        default="", description="Additional verification notes and observations"
    )