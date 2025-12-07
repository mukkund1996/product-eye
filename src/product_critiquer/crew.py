from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from .tools.persona_behavior import PersonaBehaviorTool
from .tools.report_generator import ReportGeneratorTool
from .tools.metrics_analyzer import MetricsAnalyzerTool
from .tools.playwright_tools import PlaywrightToolsWrapper
from .output_types import PersonaNavigationOutput


@CrewBase
class ProductCritiquer:
    """ProductCritiquer crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.playwright_tools = PlaywrightToolsWrapper(headless=False)

    @agent
    def persona_navigator(self) -> Agent:
        return Agent(
            config=self.agents_config["persona_navigator"],
            tools=[
                *self.playwright_tools.get_all_tools(),
                PersonaBehaviorTool(),
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
            tools=[ReportGeneratorTool(), MetricsAnalyzerTool()],
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
            output_file="product_critique_report.md",
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
            output_log_file="crew_execution.log",
        )
