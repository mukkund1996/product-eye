from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import StagehandTool, SerperDevTool
from stagehand.schemas import AvailableModel
import os
from dotenv import load_dotenv
from typing import Dict, Any

from .output_types import (
    PersonaNavigationOutput,
    PersonaResearchOutput,
    NavigationVerificationOutput,
)

# Load environment variables from .env file
load_dotenv()


@CrewBase
class ProductCritiquer:
    """ProductCritiquer crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        # Initialize StagehandTool
        browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
        browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
        model_api_key = os.environ.get("GEMINI_API_KEY")
        self.stagehand_tool = StagehandTool(
            api_key=browserbase_api_key,
            project_id=browserbase_project_id,
            model_api_key=model_api_key,
            model_name=AvailableModel.GEMINI_2_0_FLASH,
            self_heal=True,
        )

        # Initialize SerperDevTool
        self.serper_tool = SerperDevTool()

    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'stagehand_tool') and self.stagehand_tool is not None:
                self.stagehand_tool.close()
                self.stagehand_tool = None
        except Exception as e:
            # Silently handle cleanup errors - browser context might already be closed
            # This is common when the browser/context is closed by other means
            pass

    @agent
    def persona_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["persona_researcher"],
            tools=[self.serper_tool],
            memory=False,
        )

    @agent
    def persona_navigator(self) -> Agent:
        return Agent(
            config=self.agents_config["persona_navigator"],
            tools=[self.stagehand_tool],
            memory=False,
        )

    @agent
    def interviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["interviewer"],
            memory=False,
        )

    @agent
    def navigation_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["navigation_monitor"],
            memory=False,
        )

    @agent
    def report_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config["report_synthesizer"],
        )

    @task
    def persona_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["persona_research_task"],
            output_pydantic=PersonaResearchOutput,
        )

    @task
    def persona_navigation_task(self) -> Task:
        return Task(
            config=self.tasks_config["persona_navigation_task"],
            output_pydantic=PersonaNavigationOutput,
        )

    @task
    def navigation_verification_task(self) -> Task:
        return Task(
            config=self.tasks_config["navigation_verification_task"],
            output_pydantic=NavigationVerificationOutput,
        )

    @task
    def interview_simulation_task(self) -> Task:
        return Task(
            config=self.tasks_config["interview_simulation_task"],
        )

    @task
    def final_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["final_report_task"],
            output_file="output/product_critique_report_{persona_type}.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProductCritiquer crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            tracing=True,
            output_log_file="./logs/crew_execution.log",
        )

    def kickoff_with_verification(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Custom kickoff method that handles navigation verification and retries"""
        max_navigation_retries = 3  # Global retry limit for navigation task
        navigation_retry_count = 0

        # Step 1: Always run persona research first
        print("🔍 Starting persona research...")
        persona_research_crew = Crew(
            agents=[self.persona_researcher()],
            tasks=[self.persona_research_task()],
            process=Process.sequential,
            verbose=True,
            memory=False,
        )
        persona_research_result = persona_research_crew.kickoff(inputs=inputs)

        # Step 2: Navigation and verification loop
        navigation_approved = False
        navigation_result = None
        verification_result = None

        while (
            not navigation_approved and navigation_retry_count < max_navigation_retries
        ):
            navigation_retry_count += 1
            print(
                f"🧭 Starting navigation attempt {navigation_retry_count}/{max_navigation_retries}..."
            )

            # Run navigation task
            navigation_crew = Crew(
                agents=[self.persona_navigator()],
                tasks=[self.persona_navigation_task()],
                process=Process.sequential,
                verbose=True,
                memory=False,
            )
            navigation_result = navigation_crew.kickoff(inputs=inputs)

            # Run verification task
            print("✅ Starting navigation verification...")
            verification_crew = Crew(
                agents=[self.navigation_monitor()],
                tasks=[self.navigation_verification_task()],
                process=Process.sequential,
                verbose=True,
                memory=False,
            )
            verification_result = verification_crew.kickoff(inputs=inputs)

            # Parse verification decision with proper typing
            if (
                verification_result
                and hasattr(verification_result, "pydantic")
                and verification_result.pydantic
            ):
                verification_output: NavigationVerificationOutput = (
                    verification_result.pydantic
                )
                decision = verification_output.final_decision.value  # Access enum value
            else:
                # Fallback parsing if pydantic output is not available
                decision = (
                    "PROCEED"  # Default to proceed if verification format is unclear
                )

            print(f"🎯 Verification decision: {decision}")

            if decision == "PROCEED":
                navigation_approved = True
                print("✅ Navigation approved, proceeding to interview...")
            elif decision == "ACCEPTABLE_WITH_MAX_ATTEMPTS":
                navigation_approved = True
                print(
                    "⚠️ Navigation acceptable despite max attempts reached, proceeding..."
                )
            elif (
                decision == "RETRY" and navigation_retry_count < max_navigation_retries
            ):
                print(
                    f"🔄 Navigation needs retry. Attempt {navigation_retry_count + 1} will begin..."
                )
                if (
                    verification_result
                    and hasattr(verification_result, "pydantic")
                    and verification_result.pydantic
                ):
                    retry_guidance = verification_result.pydantic.retry_guidance
                    print(f"📋 Retry guidance: {retry_guidance}")
            else:
                # Max retries reached
                navigation_approved = True
                print(
                    f"⏰ Maximum navigation retries ({max_navigation_retries}) reached. Proceeding with current results..."
                )

        # Step 3: Continue with interview and final report
        print("🎤 Starting interview simulation and final report...")
        final_crew = Crew(
            agents=[self.interviewer(), self.report_synthesizer()],
            tasks=[self.interview_simulation_task(), self.final_report_task()],
            process=Process.sequential,
            verbose=True,
            memory=False,
        )
        final_result = final_crew.kickoff(inputs=inputs)

        # Return comprehensive results
        return {
            "persona_research": persona_research_result,
            "navigation_result": navigation_result,
            "verification_result": verification_result,
            "navigation_retry_count": navigation_retry_count,
            "final_result": final_result,
        }
