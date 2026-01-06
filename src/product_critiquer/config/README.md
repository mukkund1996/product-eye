# Configuration System

This directory contains the YAML-based configuration system for the Product Critiquer. All inputs must be specified through YAML configuration files.

## Configuration Format

The Product Critiquer uses **YAML configuration files exclusively** (`.yaml` or `.yml` extension). No default configuration is provided - a valid YAML configuration file is required to run the application.

### YAML Configuration Structure

```yaml
app_url: "https://example.com"
persona_type: "Full-stack developer"
testing_instructions:
  - task: "Test the main functionality"
    priority: "high"
    max_attempts: 3
    success_criteria: "Successfully navigate and understand the app"
    fallback_action: "Document any issues encountered"
  - task: "Evaluate user experience"
    priority: "medium"
    max_attempts: 2
    success_criteria: "Assess overall UX and usability"
    fallback_action: "Document UX issues and continue"
```

## Required Fields

### Top-level Configuration
- **app_url** (required): The URL of the application to test (must be a non-empty string)
- **persona_type** (required): The persona type for testing (must be a non-empty string)
- **testing_instructions** (optional): List of testing tasks

### Testing Instructions Structure
If `testing_instructions` is provided, each instruction must include:
- **task** (required): Description of what to test
- **priority** (required): "high", "medium", or "low"
- **max_attempts** (required): Maximum number of attempts for this task
- **success_criteria** (required): What constitutes success for this task
- **fallback_action** (required): What to do if the task fails

## Usage Examples

### Command Line Usage

```bash
# Run with YAML configuration (required)
python main.py --config config/examples/hackernews_config.yaml

# Run with custom YAML configuration
python main.py --config my_custom_config.yaml

# Short form
python main.py -c config/examples/stackoverflow_config.yaml
```

**Note**: A configuration file is **required**. The application will exit with an error if:
- No configuration file is provided
- The configuration file doesn't exist
- The configuration file has invalid YAML syntax
- The configuration file is missing required fields

### Programmatic Usage

```python
from product_critiquer.config.inputs import InputLoader

# Load and validate YAML configuration
try:
    inputs = InputLoader.load_and_validate('path/to/config.yaml')
    print("Configuration loaded successfully")
except Exception as e:
    print(f"Configuration error: {e}")
```

## Example Files

The `examples/` directory contains sample YAML configuration files for different scenarios:

- `hackernews_config.yaml`: HackerNews testing configuration
- `stackoverflow_config.yaml`: StackOverflow testing configuration  
- `portfolio_config.yaml`: Portfolio website testing configuration

## Validation and Error Handling

The system performs strict validation:

### File Validation
- Only `.yaml` and `.yml` files are accepted
- Files must exist and be readable
- YAML syntax must be valid

### Configuration Validation
- Required fields (`app_url`, `persona_type`) must be present and non-empty strings
- If `testing_instructions` is provided, it must be a list
- Each testing instruction must contain all required fields with appropriate types

### Error Behavior
Unlike the previous version, the system will **exit with an error** if:
- Configuration file is missing or inaccessible
- YAML syntax is invalid
- Required fields are missing or invalid
- Any validation check fails

**No fallback to default configuration is provided** - this ensures explicit configuration management.