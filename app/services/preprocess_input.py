# app/services/preprocess_input.py

import json
import os

from app.models.request import GenerateRequest
from app.services.fuzzy_matching import select_template_rule_based
from app.services.llm_service import LLMService
from app.services.sentence_embeddings import SentenceEmbeddingMatcher
from app.utils.template_loader import load_single_template


def preprocess_input(request: GenerateRequest) -> str:
    """
    Preprocesses the user input to select the best matching template and then builds
    and sends a final prompt to the LLM for synthetic data generation.

    Workflow:
      1. Try rule-based template selection.
      2. If NOT_FOUND, try sentence embedding based matching.
      3. If a template is found, load the JSON schema.
      4. Build the final prompt including:
         - User's original input.
         - A static instruction message.
         - The selected JSON schema (pretty printed).
      5. Send the prompt to the LLM API and return the generated synthetic data.
    """
    user_input = request.prompt
    # Step 1: Rule-Based Template Selection
    template_name = select_template_rule_based(user_input)
    if template_name != "NOT_FOUND":
        selected_template_name = template_name
    else:
        # Step 2: Embedding-Based Template Selection
        matcher = SentenceEmbeddingMatcher()
        template_name_from_embeddings = matcher.match_template(user_input)
        if template_name_from_embeddings != "NOT_FOUND":
            selected_template_name = template_name_from_embeddings
        else:
            # No template found by either method
            selected_template_name = "NOT_FOUND"

    # If no template was found, return early or handle accordingly.
    if selected_template_name == "NOT_FOUND":
        print("No matching template found for the input.")
        return "NOT_FOUND"

    # Step 3: Load the selected JSON template (schema)
    selected_template = load_single_template(selected_template_name)
    if not selected_template:
        print("Template file could not be loaded.")
        return "NOT_FOUND"

    # Step 4: Build the final prompt with best practices in prompt engineering.
    static_instruction = f"You are a synthetic data generator. Respond to the user request ONLY with valid {request.output_format} matching the schema:\n\n"

    final_prompt = (
        f"{static_instruction}\n\n"
        f"Schema:\n{json.dumps(selected_template, indent=2)}\n\n"
        f"User Request: {user_input}\n\n"
        f"- No explanations"
        f"- No additional text"
        f"- No markdown formatting"
        f"- Never use markdown code blocks"
        f"Ensure that any specific field modifications (if mentioned by the user) are considered."
        f"Generate 5 synthetic examples. Output pure {request.output_format} only:"
    )

    # Step 5: Send the final prompt to the LLM API
    synthetic_data = LLMService.call_llm_api(final_prompt)
    return synthetic_data


# For debugging, you can test these functions independently.
if __name__ == "__main__":
    # Example inputs:
    test_requests = [
        "Generate synthetic data for a tax free saving account",
        "I need data for a health insurance policy",
        "Produce synthetic records for dental insurances",
        "Mock data for TFSA",
        "Data generation for retirement savings",
        "Create data for a claim submission process",
        "Synthetic data for business owner insurance",
        "Generate records for critical illness coverage",
        "Mock data for disability insurance",
        "Data generation for life insurance policies",
        "Produce synthetic data for long-term care insurance",
        "Create mock records for mortgage protection",
        "Synthetic data for personal health insurance",
        "Generate data for travel insurance policies",
        "Mock data for a first home savings account",
        "Data generation for life income fund",
        "Produce synthetic records for locked-in retirement accounts",
        "Create data for registered education savings plans",
        "Synthetic data for registered retirement income funds",
        "Generate mock data for registered retirement savings plans",
        "Data generation for tax-free savings accounts",
        "I need synthetic data for a critical illness plan",
        "Produce mock records for a dental plan",
        "Create data for a disability coverage policy",
        "Generate synthetic data for a life protection plan",
        "Mock data for elder care insurance",
        "Data generation for home loan protection",
        "Synthetic data for individual health plans",
        "Produce records for trip protection insurance",
        "Create mock data for a first-time home buyer savings account",
        "Generate data for a retirement income fund",
        "Synthetic data for a pension income fund",
        "Mock data for a child education fund",
        "Data generation for a pension fund",
        "Produce synthetic records for a tax-free investment account",
    ]

    class DummyRequest:
        def __init__(self, prompt, input_format, volume):
            self.prompt = prompt
            self.input_format = input_format
            self.volume = volume

    # Testing each scenario:
    for req in test_requests:
        dummy_request = DummyRequest(prompt=req, input_format="CSV", volume=1000)
        print("Final Prompt:", preprocess_input(dummy_request))
