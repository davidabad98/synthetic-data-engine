# app/main.py
import logging
import os
import sys

from pydantic import ValidationError

from app.models.request import OutputFormat

logger = logging.getLogger(__name__)


def main_template(user_input):
    try:
        # Get the current script's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate up to the project root (app's parent)
        project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from app.models.request import GenerateRequest
        from app.services.preprocess_input import preprocess_input

        request = GenerateRequest(
            prompt=user_input,
            output_format=OutputFormat.CSV,
            volume=10,
            parameters=None,
        )

        result = preprocess_input(request)
        logger.info("preprocess_input result:", result)

        return 200, result  # Success exit code

    except ValidationError as e:
        error = f"Invalid user input: {e.errors()}"
        logger.error(f"Invalid user input: {e.errors()}")
        return 403, error
    except KeyboardInterrupt:
        error = "Process interrupted by user"
        logger.info(error)
        return 503, error
    except Exception as e:
        error = f"Unexpected error occurred: {str(e)}"
        logger.exception(error)
        return 500, error


"""
200: Success
403: Validation error
503: User interrupt
500: General error
500: Critical unhandled error
"""

if __name__ == "__main__":
    try:
        user_input = "Data generation for retirement savings"
        exit_code, _ = main_template(user_input)
    except Exception as e:
        logger.exception("Critical error in main execution:")
        exit_code = 500
    finally:
        # Add any cleanup operations here
        pass

    sys.exit(exit_code)
