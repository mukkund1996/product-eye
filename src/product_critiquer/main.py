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
