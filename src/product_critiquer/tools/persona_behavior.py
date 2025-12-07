from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import json
from typing import TypedDict


class PersonaConfig(TypedDict):
    demographics: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    timing_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    pain_points: List[str]


class PersonaBehaviorInput(BaseModel):
    """Input schema for persona behavior simulation."""

    persona_type: str = Field(
        ...,
        description="Type of persona: tech_savvy, novice, accessibility_focused, mobile_first, etc.",
    )
    scenario: str = Field(..., description="Testing scenario or user goal")
    interaction_data: str = Field(
        default="{}", description="JSON string of previous interaction data"
    )


class PersonaBehaviorTool(BaseTool):
    name: str = "Persona Behavior Simulator"
    description: str = (
        "Simulate realistic user behavior patterns based on specific persona profiles using LLM. "
        "Dynamically generates persona-driven navigation patterns, interaction sequences, and realistic user responses "
        "tailored to the specific scenario and user characteristics."
    )
    args_schema: Type[BaseModel] = PersonaBehaviorInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _run(
        self, persona_type: str, scenario: str, interaction_data: str = "{}"
    ) -> str:
        """Generate persona-specific behavior patterns and responses."""
        try:
            interaction_data_dict = (
                json.loads(interaction_data) if interaction_data else {}
            )

            persona_config = self._get_persona_config(persona_type)
            behavior_pattern = self._generate_behavior_pattern(
                persona_config, scenario, interaction_data_dict
            )

            return json.dumps(behavior_pattern, indent=2)

        except Exception as e:
            return f"Error simulating persona behavior: {str(e)}"

    def _get_persona_config(self, persona_type: str) -> Dict[str, PersonaConfig]:
        """Get configuration for specific persona type."""
        personas = {
            "tech_savvy": {
                "demographics": {
                    "age_range": "25-35",
                    "tech_proficiency": "high",
                    "device_preference": "desktop",
                    "internet_experience": "expert",
                },
                "behavior_patterns": {
                    "navigation_speed": "fast",
                    "error_tolerance": "low",
                    "exploration_tendency": "high",
                    "shortcut_usage": "frequent",
                    "multitasking": "high",
                },
                "timing_patterns": {
                    "between_actions": (0.5, 2.0),
                    "reading_time": (0.5, 1.5),
                    "decision_time": (0.2, 1.0),
                },
                "preferences": {
                    "keyboard_shortcuts": True,
                    "advanced_features": True,
                    "efficiency_focused": True,
                    "customization": True,
                },
                "pain_points": [
                    "Slow loading times",
                    "Unnecessary confirmation dialogs",
                    "Limited customization options",
                    "Lack of keyboard shortcuts",
                ],
            },
            "novice": {
                "demographics": {
                    "age_range": "45-65",
                    "tech_proficiency": "low",
                    "device_preference": "tablet",
                    "internet_experience": "beginner",
                },
                "behavior_patterns": {
                    "navigation_speed": "slow",
                    "error_tolerance": "high",
                    "exploration_tendency": "low",
                    "shortcut_usage": "rare",
                    "multitasking": "low",
                },
                "timing_patterns": {
                    "between_actions": (2.0, 5.0),
                    "reading_time": (2.0, 5.0),
                    "decision_time": (1.0, 4.0),
                },
                "preferences": {
                    "clear_instructions": True,
                    "large_buttons": True,
                    "step_by_step_guidance": True,
                    "familiar_patterns": True,
                },
                "pain_points": [
                    "Complex interfaces",
                    "Small text and buttons",
                    "Unclear error messages",
                    "Too many options at once",
                ],
            },

            "accessibility_focused": {
                "demographics": {
                    "age_range": "30-50",
                    "tech_proficiency": "medium",
                    "device_preference": "desktop",
                    "accessibility_needs": [
                        "screen_reader",
                        "high_contrast",
                        "keyboard_only",
                    ],
                },
                "behavior_patterns": {
                    "navigation_speed": "medium",
                    "error_tolerance": "medium",
                    "exploration_tendency": "methodical",
                    "keyboard_navigation": "primary",
                    "assistive_technology": True,
                },
                "timing_patterns": {
                    "between_actions": (1.5, 3.5),
                    "reading_time": (2.0, 4.0),
                    "decision_time": (1.0, 2.5),
                },
                "preferences": {
                    "keyboard_accessible": True,
                    "high_contrast": True,
                    "clear_focus_indicators": True,
                    "descriptive_alt_text": True,
                },
                "pain_points": [
                    "Inaccessible forms",
                    "Missing alt text",
                    "Poor keyboard navigation",
                    "Low contrast text",
                ],
            },
            "mobile_first": {
                "demographics": {
                    "age_range": "18-30",
                    "tech_proficiency": "high",
                    "device_preference": "mobile",
                    "usage_context": "on_the_go",
                },
                "behavior_patterns": {
                    "navigation_speed": "fast",
                    "error_tolerance": "low",
                    "exploration_tendency": "medium",
                    "touch_interactions": "primary",
                    "attention_span": "short",
                },
                "timing_patterns": {
                    "between_actions": (1.0, 3.0),
                    "reading_time": (1.0, 2.0),
                    "decision_time": (0.5, 1.5),
                },
                "preferences": {
                    "thumb_friendly": True,
                    "swipe_gestures": True,
                    "quick_actions": True,
                    "offline_capability": True,
                },
                "pain_points": [
                    "Small touch targets",
                    "Slow mobile loading",
                    "Desktop-only features",
                    "Poor touch responsiveness",
                ],
            },
        }

        return personas.get(persona_type, personas["novice"])

    def _generate_behavior_pattern(
        self, persona_config: Dict[str, Any], scenario: str, interaction_data: Dict
    ) -> Dict[str, Any]:
        """Generate behavior pattern based on persona config and scenario."""
        
        persona_type = persona_config.get('demographics', {}).get('tech_proficiency', 'unknown')
        
        # Base behavior patterns that agents can use to generate specific interactions
        behavior_pattern = {
            "persona_type": persona_type,
            "scenario": scenario,
            "persona_config": persona_config,
            "behavior_guidelines": self._get_behavior_guidelines(persona_config),
            "interaction_preferences": self._get_interaction_preferences(persona_config),
            "likely_challenges": persona_config.get("pain_points", []),
            "completion_probability": self._calculate_completion_probability(persona_config, scenario),
            "timing_patterns": persona_config.get("timing_patterns", {}),
            "device_behaviors": self._get_device_behaviors(persona_config),
            "success_factors": self._get_success_factors(persona_config),
            "agent_instructions": {
                "description": "Use this persona information to generate realistic, contextual interactions for the given scenario",
                "note": "The agent should create specific navigation paths and interaction sequences based on these behavior patterns"
            }
        }
        
        return behavior_pattern

    def _get_behavior_guidelines(self, persona_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get behavior guidelines for the persona."""
        behavior_patterns = persona_config.get("behavior_patterns", {})
        return {
            "navigation_approach": behavior_patterns.get("navigation_speed", "medium"),
            "error_handling": behavior_patterns.get("error_tolerance", "medium"),
            "exploration_style": behavior_patterns.get("exploration_tendency", "medium"),
            "multitasking_ability": behavior_patterns.get("multitasking", "medium"),
            "decision_making_speed": "fast" if behavior_patterns.get("navigation_speed") == "fast" else "deliberate"
        }
    
    def _get_interaction_preferences(self, persona_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get interaction preferences for the persona."""
        return persona_config.get("preferences", {})
    
    def _get_device_behaviors(self, persona_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get device-specific behaviors for the persona."""
        demographics = persona_config.get("demographics", {})
        device_preference = demographics.get("device_preference", "desktop")
        
        behaviors = {
            "primary_device": device_preference,
            "input_method": "touch" if device_preference == "mobile" else "mouse_keyboard",
            "screen_considerations": "small" if device_preference == "mobile" else "large"
        }
        
        # Add accessibility considerations
        if "accessibility_needs" in demographics:
            behaviors["accessibility_requirements"] = demographics["accessibility_needs"]
        
        return behaviors
    
    def _get_success_factors(self, persona_config: Dict[str, Any]) -> List[str]:
        """Get factors that contribute to successful task completion."""
        tech_proficiency = persona_config.get("demographics", {}).get("tech_proficiency", "medium")
        preferences = persona_config.get("preferences", {})
        
        factors = []
        
        if tech_proficiency == "high":
            factors.extend(["Clear navigation paths", "Efficient workflows", "Advanced features available"])
        elif tech_proficiency == "low":
            factors.extend(["Simple interface", "Clear instructions", "Large clickable elements", "Confirmation dialogs"])
        else:
            factors.extend(["Intuitive design", "Helpful tooltips", "Standard UI patterns"])
        
        # Add preference-based factors
        if preferences.get("keyboard_shortcuts"):
            factors.append("Keyboard shortcut support")
        if preferences.get("high_contrast"):
            factors.append("High contrast design")
        
        return factors

    def _calculate_completion_probability(
        self, persona_config: Dict, scenario: str
    ) -> float:
        """Calculate probability of successful task completion."""
        tech_proficiency = persona_config["demographics"].get(
            "tech_proficiency", "medium"
        )

        base_probabilities = {"high": 0.85, "medium": 0.75, "low": 0.60}

        scenario_factors = {"signup": 0.9, "purchase": 0.8, "navigation": 0.95}

        base_prob = base_probabilities.get(tech_proficiency, 0.75)

        for key, factor in scenario_factors.items():
            if key in scenario.lower():
                return min(base_prob * factor, 0.95)

        return base_prob
