from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import StagehandTool
from stagehand.schemas import AvailableModel
import os
from dotenv import load_dotenv

from .tools.persona_behavior import PersonaBehaviorTool
from .tools.report_generator import ReportGeneratorTool
from .tools.metrics_analyzer import MetricsAnalyzerTool
from .output_types import PersonaNavigationOutput

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
        model_api_key = os.environ.get("OPENAI_API_KEY")
        self.stagehand_tool = StagehandTool(
            api_key=browserbase_api_key,
            project_id=browserbase_project_id,
            model_api_key=model_api_key,
            model_name=AvailableModel.GPT_4O,
        )

    def cleanup(self):
        """Clean up resources"""
        self.stagehand_tool.close()

    @agent
    def persona_navigator(self) -> Agent:
        return Agent(
            config=self.agents_config["persona_navigator"],
            tools=[
                PersonaBehaviorTool(),
                self.stagehand_tool,
            ],
            memory=True,
        )

    @agent
    def interviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["interviewer"],
            memory=True,
        )

    @agent
    def report_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config["report_synthesizer"],
            tools=[ReportGeneratorTool()],
        )

    @task
    def persona_navigation_task(self) -> Task:
        return Task(
            config=self.tasks_config["persona_navigation_task"],
            output_pydantic=PersonaNavigationOutput,
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
            output_file="output/product_critique_report.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProductCritiquer crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            tracing=True,
            output_log_file="./logs/crew_execution.log",
        )
