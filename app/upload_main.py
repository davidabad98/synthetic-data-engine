import os
import sys

from app.services.epic import EPICPromptGenerator
from app.services.llm_service import LLMService
from app.services.request_model import RequestModel
from app.utils import utility
from config.config import (
    DEFAULT_FORMAT,
    DEFAULT_RECORD_COUNT,
    N_SAMPLES,
    S3_INPUT_BUCKET,
    SERVER_MODE,
)


def main(content, format=DEFAULT_FORMAT):

    # test
    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up to the project root (app's parent)
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Calling the EPICPromptGenerator class
    epic_generator = EPICPromptGenerator(
        content, N_SAMPLES, DEFAULT_RECORD_COUNT, format
    )

    # Generating an epic prompt
    epic_prompt = epic_generator.generate_prompt()

    # Sending a request to the model based on the model_used argument
    llm_response = LLMService.call_llm_api(epic_prompt)
    return 200, llm_response


if __name__ == "__main__":
    main("test_file_name")
