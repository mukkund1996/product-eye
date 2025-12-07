#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

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
    inputs = {"app_url": "https://news.ycombinator.com/", "persona_type": "tech_savvy"}
    # inputs = {
    #     "app_url": "https://stackoverflow.com/questions",
    #     "persona_type": "tech_savvy",
    # }

    # Create and run the crew
    result = ProductCritiquer().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL DECISION ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()
