from crewai.tools import BaseTool
from typing import Type, Dict, List, Any
from pydantic import BaseModel, Field
import json
import statistics
from datetime import datetime


class MetricsAnalyzerInput(BaseModel):
    """Input schema for metrics analysis."""
    raw_data: str = Field(..., description="JSON string containing raw metrics and testing data")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis: performance, usability, accessibility, comprehensive")
    benchmark_data: str = Field(default="{}", description="Optional benchmark data for comparison")


class MetricsAnalyzerTool(BaseTool):
    name: str = "Metrics Analyzer"
    description: str = (
        "Analyze quantitative metrics from testing data including performance, usability, "
        "and accessibility metrics. Provides statistical analysis and trend identification."
    )
    args_schema: Type[BaseModel] = MetricsAnalyzerInput
    
    def _run(self, raw_data: str, analysis_type: str = "comprehensive", benchmark_data: str = "{}") -> str:
        """Analyze metrics from testing data."""
        try:
            data = json.loads(raw_data) if raw_data else {}
            benchmarks = json.loads(benchmark_data) if benchmark_data else {}
            
            analysis = {
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_type": analysis_type,
                "metrics_summary": {},
                "performance_analysis": {},
                "usability_metrics": {},
                "accessibility_scores": {},
                "trends": {},
                "recommendations": []
            }
            
            if analysis_type in ["performance", "comprehensive"]:
                analysis["performance_analysis"] = self._analyze_performance_metrics(data, benchmarks)
            
            if analysis_type in ["usability", "comprehensive"]:
                analysis["usability_metrics"] = self._analyze_usability_metrics(data, benchmarks)
            
            if analysis_type in ["accessibility", "comprehensive"]:
                analysis["accessibility_scores"] = self._analyze_accessibility_metrics(data, benchmarks)
            
            # Generate overall metrics summary
            analysis["metrics_summary"] = self._generate_metrics_summary(analysis)
            
            # Identify trends and patterns
            analysis["trends"] = self._identify_trends(data)
            
            # Generate data-driven recommendations
            analysis["recommendations"] = self._generate_metric_recommendations(analysis)
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return f"Error analyzing metrics: {str(e)}"
    
    def _analyze_performance_metrics(self, data: Dict, benchmarks: Dict) -> Dict[str, Any]:
        """Analyze performance-related metrics."""
        performance_analysis = {
            "loading_metrics": {},
            "interaction_metrics": {},
            "efficiency_scores": {},
            "benchmark_comparison": {}
        }
        
        # Extract performance data
        if 'performance_metrics' in data:
            perf_data = data['performance_metrics']
            
            # Loading metrics analysis
            page_load_time = perf_data.get('page_load_time', 0)
            performance_analysis["loading_metrics"] = {
                "page_load_time": page_load_time,
                "load_performance_rating": self._rate_performance_metric(page_load_time, 'load_time'),
                "meets_web_vitals": page_load_time < 2.5,  # Core Web Vitals threshold
                "user_experience_impact": "Low" if page_load_time < 2.0 else "Medium" if page_load_time < 4.0 else "High"
            }
            
            # Total execution metrics
            total_time = perf_data.get('total_execution_time', 0)
            performance_analysis["interaction_metrics"] = {
                "total_session_time": total_time,
                "efficiency_rating": self._rate_performance_metric(total_time, 'session_time'),
                "automation_overhead": max(0, total_time - page_load_time)
            }
        
        # Compare against benchmarks if available
        if benchmarks and 'performance' in benchmarks:
            performance_analysis["benchmark_comparison"] = self._compare_to_benchmarks(
                performance_analysis, benchmarks['performance']
            )
        
        return performance_analysis
    
    def _analyze_usability_metrics(self, data: Dict, benchmarks: Dict) -> Dict[str, Any]:
        """Analyze usability-related metrics."""
        usability_analysis = {
            "interaction_success_rates": {},
            "user_satisfaction_indicators": {},
            "task_completion_analysis": {},
            "error_rate_analysis": {}
        }
        
        # Analyze interaction data if available
        if 'interactions' in data:
            interactions = data['interactions']
            successful_interactions = sum(1 for i in interactions if i.get('success', False))
            total_interactions = len(interactions)
            
            usability_analysis["interaction_success_rates"] = {
                "total_interactions": total_interactions,
                "successful_interactions": successful_interactions,
                "success_rate": successful_interactions / max(1, total_interactions),
                "usability_rating": self._rate_usability_metric(successful_interactions / max(1, total_interactions))
            }
        
        # Analyze error patterns
        if 'errors' in data:
            errors = data['errors']
            usability_analysis["error_rate_analysis"] = {
                "total_errors": len(errors),
                "error_types": self._categorize_errors(errors),
                "error_severity_distribution": self._analyze_error_severity(errors),
                "user_impact_score": self._calculate_error_impact_score(errors)
            }
        
        return usability_analysis
    
    def _analyze_accessibility_metrics(self, data: Dict, benchmarks: Dict) -> Dict[str, Any]:
        """Analyze accessibility compliance metrics."""
        accessibility_analysis = {
            "wcag_compliance_scores": {},
            "accessibility_violations": {},
            "compliance_trends": {},
            "improvement_potential": {}
        }
        
        # Extract WCAG compliance data
        if 'wcag_compliance' in data:
            wcag_data = data['wcag_compliance']
            compliance_scores = []
            
            for category, metrics in wcag_data.items():
                if isinstance(metrics, dict) and 'compliance_score' in metrics:
                    score = metrics['compliance_score']
                    compliance_scores.append(score)
                    
                    accessibility_analysis["wcag_compliance_scores"][category] = {
                        "score": score,
                        "percentage": score * 100,
                        "grade": self._grade_accessibility_score(score),
                        "meets_aa_standard": score >= 0.8
                    }
            
            # Overall accessibility score
            if compliance_scores:
                overall_score = statistics.mean(compliance_scores)
                accessibility_analysis["wcag_compliance_scores"]["overall"] = {
                    "score": overall_score,
                    "percentage": overall_score * 100,
                    "grade": self._grade_accessibility_score(overall_score),
                    "meets_aa_standard": overall_score >= 0.8
                }
        
        # Analyze accessibility violations
        if 'issues' in data:
            accessibility_issues = [issue for issue in data['issues'] if 'accessibility' in issue.get('category', '').lower()]
            
            accessibility_analysis["accessibility_violations"] = {
                "total_violations": len(accessibility_issues),
                "violation_severity": self._categorize_by_severity(accessibility_issues),
                "wcag_guidelines_affected": self._extract_wcag_guidelines(accessibility_issues),
                "remediation_priority": self._prioritize_accessibility_fixes(accessibility_issues)
            }
        
        return accessibility_analysis
    
    def _generate_metrics_summary(self, analysis: Dict) -> Dict[str, Any]:
        """Generate overall metrics summary."""
        summary = {
            "overall_health_score": 0.0,
            "key_metrics": {},
            "performance_indicators": {},
            "areas_of_concern": [],
            "strengths_identified": []
        }
        
        scores = []
        
        # Performance score contribution
        if 'performance_analysis' in analysis and 'loading_metrics' in analysis['performance_analysis']:
            load_time = analysis['performance_analysis']['loading_metrics'].get('page_load_time', 5)
            perf_score = max(0, min(1, (5 - load_time) / 5))  # Normalize to 0-1
            scores.append(perf_score)
            summary["key_metrics"]["performance_score"] = perf_score
        
        # Usability score contribution
        if 'usability_metrics' in analysis and 'interaction_success_rates' in analysis['usability_metrics']:
            usability_score = analysis['usability_metrics']['interaction_success_rates'].get('success_rate', 0.8)
            scores.append(usability_score)
            summary["key_metrics"]["usability_score"] = usability_score
        
        # Accessibility score contribution
        if 'accessibility_scores' in analysis and 'wcag_compliance_scores' in analysis['accessibility_scores']:
            if 'overall' in analysis['accessibility_scores']['wcag_compliance_scores']:
                accessibility_score = analysis['accessibility_scores']['wcag_compliance_scores']['overall']['score']
                scores.append(accessibility_score)
                summary["key_metrics"]["accessibility_score"] = accessibility_score
        
        # Calculate overall health score
        if scores:
            summary["overall_health_score"] = statistics.mean(scores)
        
        # Identify areas of concern and strengths
        summary["areas_of_concern"] = self._identify_concerns(analysis)
        summary["strengths_identified"] = self._identify_strengths(analysis)
        
        return summary
    
    def _rate_performance_metric(self, value: float, metric_type: str) -> str:
        """Rate performance metric based on industry standards."""
        if metric_type == 'load_time':
            if value < 1.0:
                return "Excellent"
            elif value < 2.5:
                return "Good"
            elif value < 4.0:
                return "Fair"
            else:
                return "Poor"
        elif metric_type == 'session_time':
            if value < 30:
                return "Efficient"
            elif value < 60:
                return "Acceptable"
            else:
                return "Slow"
        
        return "Unknown"
    
    def _rate_usability_metric(self, success_rate: float) -> str:
        """Rate usability metric based on success rate."""
        if success_rate >= 0.9:
            return "Excellent"
        elif success_rate >= 0.8:
            return "Good"
        elif success_rate >= 0.7:
            return "Fair"
        else:
            return "Poor"
    
    def _grade_accessibility_score(self, score: float) -> str:
        """Grade accessibility score."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def _categorize_errors(self, errors: List) -> Dict[str, int]:
        """Categorize errors by type."""
        categories = {}
        for error in errors:
            category = "Unknown"
            if "navigation" in str(error).lower():
                category = "Navigation"
            elif "timeout" in str(error).lower():
                category = "Timeout"
            elif "element" in str(error).lower():
                category = "Element Interaction"
            
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def _analyze_error_severity(self, errors: List) -> Dict[str, int]:
        """Analyze error severity distribution."""
        severity_dist = {"low": 0, "medium": 0, "high": 0}
        
        for error in errors:
            # Simple heuristic for severity
            error_str = str(error).lower()
            if "timeout" in error_str or "failed" in error_str:
                severity_dist["high"] += 1
            elif "warning" in error_str:
                severity_dist["low"] += 1
            else:
                severity_dist["medium"] += 1
        
        return severity_dist
    
    def _calculate_error_impact_score(self, errors: List) -> float:
        """Calculate user impact score based on errors."""
        if not errors:
            return 0.0
        
        # Simple scoring: more errors = higher impact
        error_count = len(errors)
        if error_count == 0:
            return 0.0
        elif error_count <= 2:
            return 0.3
        elif error_count <= 5:
            return 0.6
        else:
            return 1.0
    
    def _categorize_by_severity(self, issues: List) -> Dict[str, int]:
        """Categorize issues by severity."""
        severity_counts = {"low": 0, "medium": 0, "high": 0}
        
        for issue in issues:
            severity = issue.get('severity', 'medium')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return severity_counts
    
    def _extract_wcag_guidelines(self, issues: List) -> List[str]:
        """Extract WCAG guidelines from accessibility issues."""
        guidelines = set()
        for issue in issues:
            guideline = issue.get('guideline')
            if guideline:
                guidelines.add(guideline)
        
        return list(guidelines)
    
    def _prioritize_accessibility_fixes(self, issues: List) -> List[Dict]:
        """Prioritize accessibility fixes by impact and effort."""
        prioritized = []
        
        for issue in issues:
            priority_score = 0
            if issue.get('severity') == 'high':
                priority_score += 3
            elif issue.get('severity') == 'medium':
                priority_score += 2
            else:
                priority_score += 1
            
            prioritized.append({
                "issue": issue.get('issue', 'Unknown issue'),
                "severity": issue.get('severity', 'medium'),
                "guideline": issue.get('guideline', ''),
                "priority_score": priority_score
            })
        
        # Sort by priority score (highest first)
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized[:5]  # Return top 5 priorities
    
    def _compare_to_benchmarks(self, current_analysis: Dict, benchmark_data: Dict) -> Dict[str, str]:
        """Compare current metrics to benchmark data."""
        comparison = {}
        
        # Compare load times
        if 'loading_metrics' in current_analysis and 'page_load_time' in benchmark_data:
            current_load = current_analysis['loading_metrics'].get('page_load_time', 0)
            benchmark_load = benchmark_data['page_load_time']
            
            if current_load < benchmark_load:
                comparison['load_time'] = f"Better than benchmark by {benchmark_load - current_load:.2f}s"
            else:
                comparison['load_time'] = f"Slower than benchmark by {current_load - benchmark_load:.2f}s"
        
        return comparison
    
    def _identify_trends(self, data: Dict) -> Dict[str, Any]:
        """Identify trends and patterns in the data."""
        trends = {
            "performance_trend": "Stable",
            "error_patterns": [],
            "usage_patterns": []
        }
        
        # Analyze error patterns
        if 'errors' in data and data['errors']:
            error_types = self._categorize_errors(data['errors'])
            most_common_error = max(error_types.items(), key=lambda x: x[1]) if error_types else None
            
            if most_common_error:
                trends["error_patterns"].append(f"Most common error type: {most_common_error[0]} ({most_common_error[1]} occurrences)")
        
        # Analyze interaction patterns
        if 'interactions' in data:
            successful_actions = sum(1 for i in data['interactions'] if i.get('success', False))
            total_actions = len(data['interactions'])
            
            if total_actions > 0:
                success_rate = successful_actions / total_actions
                if success_rate > 0.8:
                    trends["usage_patterns"].append("High interaction success rate indicates good usability")
                elif success_rate < 0.6:
                    trends["usage_patterns"].append("Low interaction success rate suggests usability issues")
        
        return trends
    
    def _identify_concerns(self, analysis: Dict) -> List[str]:
        """Identify areas of concern from analysis."""
        concerns = []
        
        # Performance concerns
        if 'performance_analysis' in analysis:
            perf_data = analysis['performance_analysis']
            if 'loading_metrics' in perf_data:
                load_time = perf_data['loading_metrics'].get('page_load_time', 0)
                if load_time > 4.0:
                    concerns.append("Page load time exceeds acceptable thresholds")
        
        # Accessibility concerns
        if 'accessibility_scores' in analysis:
            acc_data = analysis['accessibility_scores']
            if 'wcag_compliance_scores' in acc_data and 'overall' in acc_data['wcag_compliance_scores']:
                overall_score = acc_data['wcag_compliance_scores']['overall']['score']
                if overall_score < 0.7:
                    concerns.append("Accessibility compliance below recommended levels")
        
        # Usability concerns
        if 'usability_metrics' in analysis:
            usability_data = analysis['usability_metrics']
            if 'interaction_success_rates' in usability_data:
                success_rate = usability_data['interaction_success_rates'].get('success_rate', 1.0)
                if success_rate < 0.8:
                    concerns.append("User interaction success rate below target")
        
        return concerns
    
    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """Identify strengths from analysis."""
        strengths = []
        
        # Performance strengths
        if 'performance_analysis' in analysis:
            perf_data = analysis['performance_analysis']
            if 'loading_metrics' in perf_data:
                load_time = perf_data['loading_metrics'].get('page_load_time', 10)
                if load_time < 2.0:
                    strengths.append("Excellent page load performance")
        
        # Accessibility strengths
        if 'accessibility_scores' in analysis:
            acc_data = analysis['accessibility_scores']
            if 'wcag_compliance_scores' in acc_data and 'overall' in acc_data['wcag_compliance_scores']:
                overall_score = acc_data['wcag_compliance_scores']['overall']['score']
                if overall_score > 0.85:
                    strengths.append("Strong accessibility compliance")
        
        return strengths
    
    def _generate_metric_recommendations(self, analysis: Dict) -> List[Dict[str, str]]:
        """Generate recommendations based on metric analysis."""
        recommendations = []
        
        # Performance recommendations
        if 'performance_analysis' in analysis:
            perf_data = analysis['performance_analysis']
            if 'loading_metrics' in perf_data:
                load_time = perf_data['loading_metrics'].get('page_load_time', 0)
                if load_time > 3.0:
                    recommendations.append({
                        "category": "Performance",
                        "priority": "High",
                        "recommendation": "Optimize page load time through code splitting, image optimization, and caching strategies",
                        "expected_impact": "Improve usability and reduce bounce rate"
                    })
        
        # Accessibility recommendations
        if 'accessibility_scores' in analysis:
            acc_data = analysis['accessibility_scores']
            if 'accessibility_violations' in acc_data:
                violations = acc_data['accessibility_violations'].get('total_violations', 0)
                if violations > 0:
                    recommendations.append({
                        "category": "Accessibility",
                        "priority": "High",
                        "recommendation": "Address accessibility violations to ensure WCAG 2.1 AA compliance",
                        "expected_impact": "Expand user base and reduce legal risk"
                    })
        
        # Usability recommendations
        if 'usability_metrics' in analysis:
            usability_data = analysis['usability_metrics']
            if 'error_rate_analysis' in usability_data:
                error_count = usability_data['error_rate_analysis'].get('total_errors', 0)
                if error_count > 2:
                    recommendations.append({
                        "category": "Usability",
                        "priority": "Medium",
                        "recommendation": "Investigate and resolve common user interaction errors",
                        "expected_impact": "Improve task completion rates and user satisfaction"
                    })
        
        return recommendations