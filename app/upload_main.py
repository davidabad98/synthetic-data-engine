import os
import sys

from app.services.epic import EPICPromptGenerator
from app.services.request_model import RequestModel
from app.utils import utility
from config.config import GENERATED_ROWS, N_SAMPLES, S3_INPUT_FILEPATH, SERVER_MODE


def main(prompt="", format="csv"):

    # test
    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up to the project root (app's parent)
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Calling the EPICPromptGenerator class
    epic_generator = EPICPromptGenerator(
        S3_INPUT_FILEPATH, N_SAMPLES, GENERATED_ROWS, format
    )

    # Generating an epic prompt
    epic_prompt = epic_generator.generate_prompt()
    # Creating an instance of the requestModel class
    sm = RequestModel()
    # Sending a request to the model based on the model_used argument
    if SERVER_MODE != "local":
        return 0, sm.send_request_bedrock(epic_prompt)
    else:
        return 0, sm.send_request_groq(epic_prompt)


if __name__ == "__main__":
    main()
