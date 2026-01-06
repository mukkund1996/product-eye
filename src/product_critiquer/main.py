#!/usr/bin/env python
import argparse
import sys
import warnings
from typing import Dict, Any

from product_critiquer.crew import ProductCritiquer
from product_critiquer.config.inputs import InputLoader

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.


def load_inputs(yaml_file_path: str) -> Dict[str, Any]:
    """
    Load inputs from YAML configuration file.
    
    Args:
        yaml_file_path: Path to YAML configuration file
    
    Returns:
        Dictionary containing the loaded and validated inputs
        
    Raises:
        SystemExit: If configuration file is missing, invalid, or has validation errors
    """
    try:
        print(f"Loading configuration from: {yaml_file_path}")
        return InputLoader.load_and_validate(yaml_file_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Please provide a valid YAML configuration file.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: Configuration validation failed - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load configuration - {e}", file=sys.stderr)
        sys.exit(1)


def run(yaml_config_path: str):
    """
    Run the research crew with inputs from YAML configuration file.
    
    Args:
        yaml_config_path: Path to YAML configuration file
    """
    inputs = load_inputs(yaml_config_path)
    
    print(f"Running with configuration:")
    print(f"  App URL: {inputs['app_url']}")
    print(f"  Persona Type: {inputs['persona_type']}")
    print(f"  Testing Instructions: {len(inputs.get('testing_instructions', []))} tasks")
    print()

    # Create and run the crew with verification
    productCritquer = ProductCritiquer()
    try:
        result = productCritquer.kickoff_with_verification(inputs=inputs)
        print("\n\n=== EXECUTION SUMMARY ===\n")
        print(f"Navigation attempts: {result['navigation_retry_count']}")
        print("\n=== FINAL RESULT ===\n")
        if result.get('final_result'):
            print(result['final_result'])
        else:
            print("Final result not available")
    finally:
        productCritquer.cleanup()


def main():
    """Command-line interface for the product critiquer."""
    parser = argparse.ArgumentParser(
        description="Product Critiquer - Analyze web applications with AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --config config/examples/stackoverflow_config.yaml
  python main.py --config my_custom_config.yaml
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        required=True,
        help='Path to YAML configuration file (required)'
    )
    
    args = parser.parse_args()
    
    run(args.config)


if __name__ == "__main__":
    main()
