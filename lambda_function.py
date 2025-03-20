import json
import os
from upload_main import main  # Import the main function from main.py
import logging

# Set up basic logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    This function will be triggered by API Gateway.
    It reads the `model_used` query parameter from the event and passes it to the main function.
    """
    try:
        # Retrieve the model_used from the query parameters in the event (API Gateway)
        model_used = event['queryStringParameters'].get('model_used', 'groq')

        # Ensure that model_used is valid (either 'titan' or 'groq')
        if model_used not in ['titan', 'groq']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Invalid model_used parameter. Please use 'titan' or 'groq'."})
            }

        # Call the main function with the model_used parameter
        destination_uri = main(model_used=model_used)

        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f"Output data {destination_uri}"})
        }

    except Exception as e:
        error_message = str(e)
        # Log the error details
        error_message = str(e)
        logger.error(f"Error occurred: {error_message}")
        logger.error("Event data: %s", json.dumps(event))  # Log the event that triggered the error

        print(f"Error occurred: {error_message}")
        # Handle errors gracefully
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_message})
        }