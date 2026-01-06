"""
Configuration module for product critiquer inputs.
"""

from typing import Dict, Any
import json
import yaml
import importlib.util
from pathlib import Path


class InputLoader:
    """Handles loading inputs from various sources."""

    @staticmethod
    def load_from_json(file_path: str) -> Dict[str, Any]:
        """Load inputs from a JSON file."""
        with open(file_path, "r") as f:
            return json.load(f)

    @staticmethod
    def load_from_yaml(file_path: str) -> Dict[str, Any]:
        """Load inputs from a YAML file."""
        with open(file_path, "r") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_from_module(module_path: str) -> Dict[str, Any]:
        """Load inputs from a Python module."""
        spec = importlib.util.spec_from_file_location("input_config", module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for common input variable names
        if hasattr(module, "INPUTS"):
            return module.INPUTS
        elif hasattr(module, "inputs"):
            return module.inputs
        elif hasattr(module, "config"):
            return module.config
        else:
            # If no standard name found, return all module attributes that don't start with _
            return {k: v for k, v in module.__dict__.items() if not k.startswith("_")}

    @staticmethod
    def auto_detect_and_load(file_path: str) -> Dict[str, Any]:
        """Auto-detect file type and load inputs accordingly."""
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".json":
            return InputLoader.load_from_json(file_path)
        elif extension in [".yaml", ".yml"]:
            return InputLoader.load_from_yaml(file_path)
        elif extension == ".py":
            return InputLoader.load_from_module(file_path)
        else:
            raise ValueError(
                f"Unsupported file type: {extension}. Supported types: .json, .yaml, .yml, .py"
            )

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """Validate that the configuration has required fields."""
        required_fields = ['app_url', 'persona_type']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in configuration")
            if not config[field] or not isinstance(config[field], str):
                raise ValueError(f"Field '{field}' must be a non-empty string")
        
        # Validate testing_instructions if present
        if 'testing_instructions' in config:
            if not isinstance(config['testing_instructions'], list):
                raise ValueError("Field 'testing_instructions' must be a list")
            
            for i, instruction in enumerate(config['testing_instructions']):
                if not isinstance(instruction, dict):
                    raise ValueError(f"Testing instruction {i} must be a dictionary")
                
                required_instruction_fields = ['task', 'priority', 'max_attempts', 'success_criteria', 'fallback_action']
                for field in required_instruction_fields:
                    if field not in instruction:
                        raise ValueError(f"Missing required field '{field}' in testing instruction {i}")

    @staticmethod
    def load_and_validate(file_path: str) -> Dict[str, Any]:
        """Load and validate YAML configuration."""
        # Check file extension
        path = Path(file_path)
        if path.suffix.lower() not in ['.yaml', '.yml']:
            raise ValueError(f"Only YAML files (.yaml, .yml) are supported. Got: {path.suffix}")
        
        try:
            # Load configuration
            config = InputLoader.load_from_yaml(file_path)
            if config is None:
                raise ValueError(f"YAML file {file_path} is empty or invalid")
            
            # Validate configuration
            InputLoader.validate_config(config)
            
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax in {file_path}: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise  # Re-raise validation errors as-is
            raise RuntimeError(f"Error loading configuration from {file_path}: {e}")
