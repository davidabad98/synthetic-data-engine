import json
import logging
import os

from app.main import main_template
from app.upload_main import main  # Import the main function from main.py
from config.config import SERVER_FLOW

logger = logging.getLogger(__name__)


# Uncomment this for AWS cloud Lambda implementation:
# def lambda_handler(event, context):
def lambda_handler(request, event="", context=""):
    """
    This function will be triggered by API Gateway.
    It reads the `model_used` query parameter from the event and passes it to the main function.
    """
    try:
        # Decide between flow 1 OR 2
        # if SERVER_FLOW == 1:
        if request.prompt != "epic-generation":
            logger.info(f"Started template-generation")
            status_code, result = main_template(user_input=request.prompt)
        else:
            logger.info(f"Started epic-generation.")
            status_code, result = main()

        result_message = (
            f"Data successfully generated! You can access it here: {result}"
            if status_code == 0
            else result
        )

        # Return a success response
        return {
            "statusCode": 200,
            "body": json.dumps({"data": f"{result_message}"}),
        }

    except Exception as e:
        error_message = str(e)
        # Log the error details
        error_message = str(e)
        logger.error(f"Error occurred: {error_message}")
        logger.error(
            "Event data: %s", json.dumps(event)
        )  # Log the event that triggered the error

        logger.error(f"Error occurred: {error_message}")
        # Handle errors gracefully
        return {"statusCode": 500, "body": json.dumps({"error": error_message})}


if __name__ == "__main__":
    request = "Generate synthetic data for a tax free saving account"
    lambda_handler(request)
