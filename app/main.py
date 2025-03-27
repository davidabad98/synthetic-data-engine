# app/main.py
import logging
import os
import sys

from pydantic import ValidationError

from config.config import SERVER_FLOW

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main_template():
    try:
        # Get the current script's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate up to the project root (app's parent)
        project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from app.models.request import GenerateRequest
        from app.services.preprocess_input import preprocess_input

        user_input = "i want to generate syntheic data for a dental insurances and give me 10 rows"
        # user_input = "buy burgers and fries"

        request = GenerateRequest(prompt=user_input, output_format="csv", volume=10)

        result = preprocess_input(request)
        print("Generated Synthetic Data:", result)

        return 0  # Success exit code

    except ValidationError as e:
        logger.error(f"Invalid user input: {e.errors()}")
        return 1
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 2
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        return 3


"""
0: Success
1: Validation error
2: User interrupt
3: General error
4: Critical unhandled error
"""

if __name__ == "__main__":
    try:
        exit_code = main_template()
    except Exception as e:
        logger.exception("Critical error in main execution:")
        exit_code = 4
    finally:
        # Add any cleanup operations here
        pass

    sys.exit(exit_code)
