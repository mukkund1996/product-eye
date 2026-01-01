#!/usr/bin/env python
import warnings

from product_critiquer.crew import ProductCritiquer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the research crew.
    """
    inputs = {
        "app_url": "https://news.ycombinator.com/",
        "persona_type": "Full-stack developer",
        "testing_instructions": [
            {
                "task": "Explore the main interface and understand the primary purpose",
                "priority": "high",
                "max_attempts": 3,
                "success_criteria": "Gain understanding of what the application does and how to navigate it",
                "fallback_action": "Document any confusion about the application's purpose and continue",
            },
            {
                "task": "Participate in the community discussion features",
                "priority": "medium",
                "max_attempts": 2,
                "success_criteria": "Understand and attempt to engage with community interaction features",
                "fallback_action": "Document participation barriers and observe community interactions passively",
            },
            {
                "task": "Evaluate the user experience for finding valuable information",
                "priority": "medium",
                "max_attempts": 3,
                "success_criteria": "Assess how effectively the platform helps users discover useful content",
                "fallback_action": "Document information discovery challenges and continue with available features",
            },
            {
                "task": "Test content categorization and filtering capabilities",
                "priority": "high",
                "max_attempts": 3,
                "success_criteria": "Understand how content is categorized (e.g., by topic, time, popularity) and test any available filtering options",
                "fallback_action": "Document the categorization system observed and any limitations in content organization",
            },
            {
                "task": "Evaluate search functionality and content discoverability",
                "priority": "high",
                "max_attempts": 3,
                "success_criteria": "Test search features, explore how to find specific topics or articles, and assess search result quality",
                "fallback_action": "Document search limitations and alternative methods for finding specific content",
            },
            {
                "task": "Analyze content organization and ranking system",
                "priority": "medium",
                "max_attempts": 2,
                "success_criteria": "Understand how stories are ranked, ordered, and organized on the main page and category pages",
                "fallback_action": "Document observed patterns in content organization without full understanding of ranking mechanisms",
            },
            {
                "task": "Evaluate content tagging and topic organization",
                "priority": "low",
                "max_attempts": 2,
                "success_criteria": "Assess how well content is tagged or grouped by topics, and test navigation between related content",
                "fallback_action": "Document the topic organization system or lack thereof, and continue with other evaluation tasks",
            },
        ],
    }

    # inputs = {
    #     "app_url": "https://stackoverflow.com",
    #     "persona_type": "Full-stack developer",
    # }

    # inputs = {"app_url": "https://thisismukkunds.site/", "persona_type": "Full-stack developer"}

    # Create and run the crew
    productCritquer = ProductCritiquer()
    try:
        result = productCritquer.crew().kickoff(inputs=inputs)
    finally:
        productCritquer.cleanup()

    # Print the result
    print("\n\n=== FINAL DECISION ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()
