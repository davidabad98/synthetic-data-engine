import json
import os
from upload_main import main  # Import the main function from main.py

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
        main(model_used=model_used)

        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f"Successfully triggered {model_used} model!"})
        }

    except Exception as e:
        # Handle errors gracefully
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
