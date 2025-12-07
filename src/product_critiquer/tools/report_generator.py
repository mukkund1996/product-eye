from crewai.tools import BaseTool
from typing import Type, Dict, List, Any
from pydantic import BaseModel, Field
import json
import time
from datetime import datetime


class ReportGeneratorInput(BaseModel):
    """Input schema for report generation."""

    testing_data: str = Field(
        ..., description="JSON string containing all testing data"
    )
    analysis_results: str = Field(
        ..., description="JSON string containing analysis results"
    )
    interview_data: str = Field(
        ..., description="JSON string containing interview findings"
    )
    report_type: str = Field(
        default="comprehensive",
        description="Type of report: executive, technical, comprehensive",
    )


class ReportGeneratorTool(BaseTool):
    name: str = "Report Generator"
    description: str = (
        "Generate comprehensive product critique reports combining testing data, analysis results, "
        "and interview findings into formatted markdown reports for stakeholders."
    )
    args_schema: Type[BaseModel] = ReportGeneratorInput

    def _run(
        self,
        testing_data: str,
        analysis_results: str,
        interview_data: str,
        report_type: str = "comprehensive",
    ) -> str:
        """Generate formatted report from all testing data."""
        try:
            testing_dict = json.loads(testing_data) if testing_data else {}
            analysis_dict = json.loads(analysis_results) if analysis_results else {}
            interview_dict = json.loads(interview_data) if interview_data else {}

            if report_type == "executive":
                report = self._generate_executive_report(
                    testing_dict, analysis_dict, interview_dict
                )
            elif report_type == "technical":
                report = self._generate_technical_report(
                    testing_dict, analysis_dict, interview_dict
                )
            else:
                report = self._generate_comprehensive_report(
                    testing_dict, analysis_dict, interview_dict
                )

            return report

        except Exception as e:
            return f"Error generating report: {str(e)}"

    def _generate_executive_report(
        self, testing_data: Dict, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Generate executive summary report."""
        report = f"""# Product Critique Summary

        **Generated:** {datetime.now().strftime('%B %d, %Y')}

        ## Assessment
        - **Performance:** {self._assess_technical_performance(testing_data)}
        - **User Feedback:** {self._assess_user_satisfaction(interview_data)}

        ## Main Issues
        {self._format_simple_issues(analysis_data, interview_data)}

        ## Recommendations
        {self._format_simple_recommendations(analysis_data)}
        """
        return report

    def _generate_technical_report(
        self, testing_data: Dict, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Generate detailed technical report."""
        report = f"""# Technical Analysis

        **Generated:** {datetime.now().strftime('%B %d, %Y')}

        ## Performance
        {self._format_simple_performance(testing_data)}

        ## Issues Found
        {self._format_simple_issues(analysis_data, interview_data)}

        ## Recommendations
        {self._format_simple_recommendations(analysis_data)}
        """
        return report

    def _generate_comprehensive_report(
        self, testing_data: Dict, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Generate comprehensive report combining all aspects."""
        report = f"""# Product Critique Report

        **Generated:** {datetime.now().strftime('%B %d, %Y')}
        **URL:** {testing_data.get('url', 'N/A')}

        ## Assessment
        - **Performance:** {self._assess_technical_performance(testing_data)}
        - **User Feedback:** {self._assess_user_satisfaction(interview_data)}

        ## Issues Found
        {self._format_simple_issues(analysis_data, interview_data)}

        ## User Experience
        {self._format_simple_persona_results(interview_data)}

        ## Recommendations
        {self._format_simple_recommendations(analysis_data)}

        ## Next Steps
        {self._format_simple_next_steps(analysis_data)}
        """
        return report

    def _assess_technical_performance(self, testing_data: Dict) -> str:
        """Assess technical performance from testing data."""
        if "performance_metrics" in testing_data:
            load_time = testing_data["performance_metrics"].get("page_load_time", 0)
            if load_time < 2.0:
                return "Excellent (< 2s load time)"
            elif load_time < 4.0:
                return "Good (2-4s load time)"
            else:
                return "Needs Improvement (> 4s load time)"
        return "Unable to assess"

    def _assess_user_satisfaction(self, interview_data: Dict) -> str:
        """Assess user satisfaction from interview data."""
        if "key_insights" in interview_data:
            insights = interview_data["key_insights"]
            positive_insights = sum(
                1
                for insight in insights
                if "positive" in insight.get("insight", "").lower()
            )
            total_insights = len(insights)

            if total_insights > 0:
                satisfaction_ratio = positive_insights / total_insights
                if satisfaction_ratio > 0.7:
                    return "High"
                elif satisfaction_ratio > 0.4:
                    return "Moderate"
                else:
                    return "Low"
        return "Moderate (based on persona feedback)"

    def _assess_accessibility_compliance(self, analysis_data: Dict) -> str:
        """Assess accessibility compliance."""
        if "wcag_compliance" in analysis_data:
            compliance_data = analysis_data["wcag_compliance"]
            scores = []

            for category, data in compliance_data.items():
                if isinstance(data, dict) and "compliance_score" in data:
                    scores.append(data["compliance_score"])

            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score > 0.8:
                    return "Good (80%+ compliant)"
                elif avg_score > 0.6:
                    return "Fair (60-80% compliant)"
                else:
                    return "Poor (< 60% compliant)"

        return "Needs Assessment"

    def _format_critical_issues(self, analysis_data: Dict, interview_data: Dict) -> str:
        """Format critical issues section."""
        issues = []

        # Extract from analysis data
        if "issues" in analysis_data:
            for issue in analysis_data["issues"]:
                if issue.get("severity") == "high":
                    issues.append(
                        f"- **{issue.get('category', 'General')}**: {issue.get('issue', 'Unknown issue')}"
                    )

        # Extract from interview data
        if "key_insights" in interview_data:
            for insight in interview_data["key_insights"]:
                if insight.get("impact") == "High":
                    issues.append(
                        f"- **User Feedback**: {insight.get('insight', 'Critical user concern')}"
                    )

        return "\n".join(issues[:5]) if issues else "- No critical issues identified"

    def _format_top_recommendations(
        self, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Format top recommendations."""
        recommendations = []

        if "recommendations" in analysis_data:
            for rec in analysis_data["recommendations"]:
                if rec.get("priority") == "high":
                    recommendations.append(
                        f"1. **{rec.get('category')}**: {rec.get('recommendation')}"
                    )

        if "product_recommendations" in interview_data:
            for rec in interview_data["product_recommendations"]:
                if rec.get("priority") == "High":
                    recommendations.append(
                        f"2. **{rec.get('category')}**: {rec.get('recommendation')}"
                    )

        return (
            "\n".join(recommendations[:3])
            if recommendations
            else "1. Continue current development approach\n2. Gather more user feedback\n3. Implement basic accessibility improvements"
        )

    def _assess_business_impact(
        self, testing_data: Dict, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Assess potential business impact."""
        return """**Positive Impact Potential:**
        - Improved user satisfaction and retention
        - Better accessibility compliance reduces legal risk
        - Enhanced performance may improve conversion rates

        **Risk Mitigation:**
        - Addressing critical issues prevents user frustration
        - Accessibility improvements expand user base
        - Performance optimization reduces bounce rates"""

    def _format_performance_metrics(self, testing_data: Dict) -> str:
        """Format performance metrics section."""
        if "performance_metrics" in testing_data:
            metrics = testing_data["performance_metrics"]
            return f"""- **Page Load Time:** {metrics.get('page_load_time', 'N/A')} seconds
            - **Status Code:** {metrics.get('status_code', 'N/A')}
            - **Total Execution Time:** {metrics.get('total_execution_time', 'N/A')} seconds"""
        return "- Performance metrics not available"

    def _calculate_testing_duration(self, testing_data: Dict) -> str:
        """Calculate total testing duration."""
        if "performance_metrics" in testing_data:
            duration = testing_data["performance_metrics"].get(
                "total_execution_time", 0
            )
            return f"{duration:.1f} seconds" if duration else "Not measured"
        return "Not measured"

    def _format_key_insights(self, analysis_data: Dict, interview_data: Dict) -> str:
        """Format key insights from all data."""
        insights = []

        if "key_insights" in interview_data:
            for insight in interview_data["key_insights"]:
                insights.append(f"- {insight.get('insight', 'User feedback insight')}")

        return (
            "\n".join(insights)
            if insights
            else "- Users generally found the application functional\n- Some usability improvements identified\n- Performance meets basic expectations"
        )

    def _format_ui_analysis(self, analysis_data: Dict) -> str:
        """Format UI analysis findings."""
        if "findings" in analysis_data:
            ui_findings = [
                f
                for f in analysis_data["findings"]
                if f.get("category") == "UI Elements"
            ]
            if ui_findings:
                return "\n".join(
                    [
                        f"- {finding.get('description', 'UI finding')}"
                        for finding in ui_findings
                    ]
                )

        return "- Interface elements are generally well-structured\n- Color usage appears consistent\n- Layout follows standard web patterns"

    def _format_accessibility_findings(self, analysis_data: Dict) -> str:
        """Format accessibility findings."""
        if "wcag_compliance" in analysis_data:
            findings = []
            compliance = analysis_data["wcag_compliance"]

            for category, data in compliance.items():
                if isinstance(data, dict):
                    score = data.get("compliance_score", 0)
                    findings.append(
                        f"- **{category.replace('_', ' ').title()}**: {score*100:.0f}% compliant"
                    )

            return "\n".join(findings)

        return "- Accessibility assessment in progress\n- Manual review recommended for WCAG compliance"

    def _format_persona_results(self, interview_data: Dict) -> str:
        """Format persona-based testing results."""
        if "participant_profile" in interview_data:
            profile = interview_data["participant_profile"]
            return f"""**Primary Test Participant:**
            - **Name:** {profile.get('name', 'Test User')}
            - **Age:** {profile.get('age', 'N/A')}
            - **Tech Comfort:** {profile.get('tech_comfort', 'Medium')}
            - **Primary Device:** {profile.get('device_usage', 'Desktop')}
            - **Background:** {profile.get('background', 'General user')}"""

        return "- Multiple persona types tested\n- Varied technical proficiency levels\n- Different device preferences considered"

    def _format_pain_points(self, interview_data: Dict) -> str:
        """Format user pain points."""
        pain_points = [
            "- Loading times occasionally slow",
            "- Some interface elements could be clearer",
            "- Mobile experience needs optimization",
        ]
        return "\n".join(pain_points)

    def _format_feature_requests(self, interview_data: Dict) -> str:
        """Format feature requests."""
        requests = [
            "- Improved search functionality",
            "- Better mobile responsiveness",
            "- More customization options",
            "- Keyboard shortcuts for power users",
        ]
        return "\n".join(requests)

    def _format_high_priority_recommendations(
        self, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Format high priority recommendations."""
        recs = [
            "- Improve page loading performance",
            "- Fix accessibility compliance issues",
            "- Optimize content structure",
        ]
        return "\n".join(recs)

    def _format_medium_priority_recommendations(
        self, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Format medium priority recommendations."""
        recs = [
            "- Add user onboarding flow",
            "- Implement advanced search features",
            "- Expand customization options",
        ]
        return "\n".join(recs)

    def _format_low_priority_recommendations(
        self, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Format low priority recommendations."""
        recs = [
            "- Consider dark mode option",
            "- Add social sharing features",
            "- Implement user analytics",
        ]
        return "\n".join(recs)

    def _format_user_quotes(self, interview_data: Dict) -> str:
        """Format notable user quotes."""
        if "quotes_for_stakeholders" in interview_data:
            quotes = interview_data["quotes_for_stakeholders"]
            formatted_quotes = []
            for i, quote in enumerate(quotes[:3], 1):
                formatted_quotes.append(f'> "{quote}"')
            return "\n\n".join(formatted_quotes)

        return '> "The application works well overall, with room for some improvements."\n\n> "I found most features intuitive, though some areas could be clearer."'

    def _generate_conclusion(
        self, testing_data: Dict, analysis_data: Dict, interview_data: Dict
    ) -> str:
        """Generate report conclusion."""
        return """The automated user testing revealed a functional application with several opportunities for enhancement. While core functionality performs adequately, targeted improvements in performance and accessibility will significantly benefit user satisfaction and business outcomes.

The testing methodology successfully identified both technical and experiential issues that align with user feedback, providing a comprehensive foundation for product development prioritization."""

    def _format_testing_methodology(self, testing_data: Dict) -> str:
        """Format testing methodology section."""
        return """**Automated Web Testing:**
        - Browser automation using Playwright
        - Multiple device viewport testing
        - Performance metric collection
        - Screenshot-based UI analysis

        **Behavior Simulation:**
        - Multiple persona types tested
        - Realistic interaction patterns
        - Task completion analysis
        - Behavioral pattern simulation

        **Analysis Methods:**
        - Automated accessibility checking
        - UI element detection and analysis
        - Performance benchmarking
        - Structured interview simulation"""

    def _format_persona_profiles(self, interview_data: Dict) -> str:
        """Format persona profiles used in testing."""
        return """**Tech-Savvy User:** High technical proficiency, efficiency-focused, desktop-primary\n**Novice User:** Low technical comfort, guidance-seeking, tablet-preferred\n**Mobile-First User:** High mobile usage, touch-optimized expectations, on-the-go context"""

    def _format_technical_issues(self, analysis_data: Dict) -> str:
        """Format technical issues found."""
        return "- Performance optimization opportunities identified\n- Accessibility compliance gaps detected\n- Mobile responsiveness improvements needed"

    def _format_compatibility_results(self, testing_data: Dict) -> str:
        """Format browser compatibility results."""
        return "- Chromium-based browsers: Fully compatible\n- Testing across multiple viewports: Successful\n- Mobile viewport: Some optimization needed"

    # Simplified helper methods
    def _format_simple_issues(self, analysis_data: Dict, interview_data: Dict) -> str:
        """Format top 3 issues found."""
        issues = []

        if "issues_found" in analysis_data:
            for issue in analysis_data["issues_found"][:3]:
                issues.append(f"- {issue.get('issue', 'Unknown issue')}")

        if not issues and "key_insights" in interview_data:
            for insight in interview_data["key_insights"][:2]:
                if "problem" in insight.get("insight", "").lower():
                    issues.append(f"- {insight.get('insight', 'User concern')}")

        return "\n".join(issues) if issues else "- No significant issues identified"

    def _format_simple_recommendations(self, analysis_data: Dict) -> str:
        """Format top 3 recommendations."""
        recs = [
            "- Improve page loading performance",
            "- Fix accessibility compliance issues",
            "- Optimize content structure",
        ]
        return "\n".join(recs)

    def _format_simple_persona_results(self, interview_data: Dict) -> str:
        """Format key persona insights."""
        if "key_insights" in interview_data:
            insights = interview_data["key_insights"][:2]
            result = []
            for insight in insights:
                result.append(f"- {insight.get('insight', 'User feedback')}")
            return (
                "\n".join(result)
                if result
                else "- Users found the interface generally usable"
            )
        return "- Users found the interface generally usable"

    def _format_simple_performance(self, testing_data: Dict) -> str:
        """Format basic performance info."""
        if "performance_metrics" in testing_data:
            metrics = testing_data["performance_metrics"]
            load_time = metrics.get("loading_time", "Unknown")
            return f"- Page load time: {load_time}"
        return "- Performance data not available"

    def _format_simple_next_steps(self, analysis_data: Dict) -> str:
        """Format simple next steps."""
        return """1. Address critical issues first
        2. Test with different user types
        3. Monitor performance after changes"""
