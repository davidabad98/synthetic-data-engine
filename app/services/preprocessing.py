# app/services/preprocessing.py

from app.models.request import GenerateRequest


def preprocess_input(request: GenerateRequest) -> str:
    """
    Process user input to create a dynamic prompt.
    This includes auto-detection, normalization, and integration with a base template.
    """
    # For a prototype, we simulate combining a base template with the user prompt.
    base_template = "Base Template: Generate synthetic data with defined fields."

    final_prompt = (
        f"{base_template} "
        f"User Prompt: {request.prompt}. "
        f"Volume: {request.volume} records. "
        f"Format: {request.input_format}."
    )

    if request.parameters:
        final_prompt += f" Additional Parameters: {request.parameters}."

    return final_prompt
