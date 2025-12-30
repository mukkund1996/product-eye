from crewai.tools import BaseTool
from typing import Type, Dict, List, Any
from pydantic import BaseModel, Field
import json
from datetime import datetime


class ReportGeneratorInput(BaseModel):
    """Input schema for report generation."""

    testing_data: str = Field(
        ..., description="JSON string containing all testing data"
    )
    interview_data: str = Field(
        ..., description="JSON string containing interview findings"
    )


class ReportGeneratorTool(BaseTool):
    name: str = "Report Generator"
    description: str = (
        "Generate simple product critique reports combining testing data, analysis results, "
        "and interview findings into formatted markdown reports."
    )
    args_schema: Type[BaseModel] = ReportGeneratorInput

    def _run(
        self,
        testing_data: str,
        interview_data: str,
    ) -> str:
        """Generate formatted report from all testing data."""
        try:
            testing_dict = json.loads(testing_data) if testing_data else {}
            interview_dict = json.loads(interview_data) if interview_data else {}

            report = self._generate_report(testing_dict, interview_dict)
            return report

        except Exception as e:
            return f"Error generating report: {str(e)}"

    def _generate_report(
        self, testing_data: Dict, interview_data: Dict
    ) -> str:
        """Generate simple product critique report."""
        url = testing_data.get('url', 'N/A')
        
        report = f"""# Product Critique Report

**Generated:** {datetime.now().strftime('%B %d, %Y')}
**URL:** {url}

## Performance Assessment
{self._format_performance(testing_data)}

## Key Issues Found
{self._format_issues(testing_data, interview_data)}

## User Feedback Highlights
{self._format_user_feedback(interview_data)}

## Recommendations
{self._format_recommendations(interview_data)}
"""
        return report

    def _format_performance(self, testing_data: Dict) -> str:
        """Format basic performance metrics."""
        if "performance_metrics" in testing_data:
            metrics = testing_data["performance_metrics"]
            load_time = metrics.get('page_load_time', 'Unknown')
            status = metrics.get('status_code', 'Unknown')
            return f"- Page load time: {load_time} seconds\n- Status code: {status}"
        return "- Performance metrics not available"

    def _format_issues(self, testing_data: Dict, interview_data: Dict) -> str:
        """Format key issues identified."""
        issues = []
        
        # Get issues from testing data (errors, performance issues, etc.)
        if "errors" in testing_data:
            for error in testing_data["errors"][:2]:
                issues.append(f"- Testing issue: {error.get('message', 'Unknown error')}")
        
        # Get critical insights from interviews
        if "key_insights" in interview_data:
            for insight in interview_data["key_insights"][:2]:
                if any(word in insight.get('insight', '').lower() for word in ['problem', 'issue', 'difficult', 'confusing']):
                    issues.append(f"- User concern: {insight.get('insight', 'User feedback')}")
        
        return "\n".join(issues) if issues else "- No significant issues identified"

    def _format_user_feedback(self, interview_data: Dict) -> str:
        """Format key user feedback points."""
        feedback = []
        
        if "key_insights" in interview_data:
            for insight in interview_data["key_insights"][:3]:
                feedback.append(f"- {insight.get('insight', 'User feedback point')}")
        
        if "participant_profile" in interview_data:
            profile = interview_data["participant_profile"]
            feedback.append(f"- Tested with {profile.get('name', 'user')} ({profile.get('tech_comfort', 'medium')} tech comfort)")
        
        return "\n".join(feedback) if feedback else "- User testing completed with positive overall feedback"

    def _format_recommendations(self, interview_data: Dict) -> str:
        """Format simple recommendations based on user feedback."""
        recommendations = []
        
        # Get recommendations from interview data
        if "recommendations" in interview_data:
            for rec in interview_data["recommendations"][:3]:
                recommendations.append(f"- {rec.get('recommendation', rec.get('description', 'Improve user experience'))}")
        
        # Add basic recommendations based on common user feedback patterns
        if not recommendations:
            recommendations = [
                "- Monitor and improve page loading performance",
                "- Continue gathering user feedback for iterative improvements", 
                "- Focus on addressing any critical user experience issues"
            ]
        
        return "\n".join(recommendations)
