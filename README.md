# ProductCritiquer Crew

Welcome to the ProductCritiquer Crew project, powered by [crewAI](https://crewai.com). This multi-agent AI system performs automated product critiquing through web navigation, persona-based user testing, and comprehensive report generation.

## Overview

The ProductCritiquer Crew consists of specialized AI agents that:
- **Persona Researcher**: Uses SerperDevTool to research and build comprehensive persona profiles for different professional types (engineers, lawyers, accountants, etc.) by gathering real-world behavioral data
- **Persona Navigator**: Uses StagehandTool to navigate web applications with researched user personas, simulating realistic user behavior patterns and identifying usability issues
- **Interviewer**: Conducts simulated user interviews based on persona research and navigation findings
- **Report Synthesizer**: Creates comprehensive product critique reports with actionable insights

The system uses dynamic persona research to create authentic user testing scenarios, replacing static persona configurations with real-world data gathered through web search. This ensures more accurate and contextually relevant user behavior simulation.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Configuration

**Environment Variables**

Create a `.env` file in the root directory with the following configuration:

```bash
# Browserbase API Configuration (required for StagehandTool)
BROWSERBASE_API_KEY=your_browserbase_api_key_here
BROWSERBASE_PROJECT_ID=your_browserbase_project_id_here

# SerperDev API Configuration (required for persona research)
SERPER_API_KEY=your_serper_api_key_here

# LLM API Key (required for StagehandTool - use either Anthropic or OpenAI)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
# OPENAI_API_KEY=your_openai_api_key_here
```

**Getting API Keys:**
- **Browserbase**: Sign up at [browserbase.com](https://browserbase.com) to get your API key and project ID
- **SerperDev**: Get your API key from [serper.dev](https://serper.dev) for web search functionality
- **Anthropic**: Get your API key from [console.anthropic.com](https://console.anthropic.com)
- **OpenAI**: Get your API key from [platform.openai.com](https://platform.openai.com)

### Customizing

**YAML Configuration System**

The ProductCritiquer uses a **YAML-only configuration system**. You must provide a valid YAML configuration file to run the application - no default configuration is provided.

**Required Configuration Structure:**
```yaml
app_url: "https://example.com"
persona_type: "Full-stack developer"
testing_instructions:  # optional
  - task: "Description of what to test"
    priority: "high|medium|low"
    max_attempts: 3
    success_criteria: "What constitutes success"
    fallback_action: "What to do if task fails"
```

**Example configurations are provided in** `src/product_critiquer/config/examples/`:
- `hackernews_config.yaml` - HackerNews testing configuration
- `stackoverflow_config.yaml` - StackOverflow testing configuration
- `portfolio_config.yaml` - Portfolio website testing configuration

**Agent and Task Configuration:**
- Modify `src/product_critiquer/config/agents.yaml` to define your agents
- Modify `src/product_critiquer/config/tasks.yaml` to define your tasks
- Modify `src/product_critiquer/crew.py` to add your own logic, tools and specific args

For detailed configuration documentation, see `src/product_critiquer/config/README.md`.

## Running the Project

**YAML Configuration Required**

The application now requires a YAML configuration file. You must specify the configuration file using the `--config` parameter:

```bash
# Run with provided example configurations
python src/product_critiquer/main.py --config src/product_critiquer/config/examples/hackernews_config.yaml
python src/product_critiquer/main.py --config src/product_critiquer/config/examples/stackoverflow_config.yaml
python src/product_critiquer/main.py --config src/product_critiquer/config/examples/portfolio_config.yaml

# Run with your custom YAML configuration
python src/product_critiquer/main.py --config my_custom_config.yaml

# Short form
python src/product_critiquer/main.py -c my_config.yaml
```

**Error Handling:**
- The application will exit with an error if no configuration file is provided
- Invalid YAML syntax or missing required fields will cause the application to exit
- No fallback to default configuration is provided

**Using CrewAI CLI (Legacy Method)**

To use the original method, run this from the root folder:

```bash
$ crewai run
```

This command initializes the product_critiquer Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The product_critiquer Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the ProductCritiquer Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
