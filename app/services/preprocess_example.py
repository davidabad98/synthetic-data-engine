# app/services/preprocessing.py

import csv
import io
import json
import logging
import os
import xml.etree.ElementTree as ET
from typing import Any, Tuple, Union

from app.models.request import GenerateRequest

logger = logging.getLogger(__name__)
# Predefined field mapping for normalization
FIELD_MAPPINGS = {
    "FullName": ["FirstName", "LastName", "Name", "FullName"],
    "CustomerEmail": ["Email", "EmailAddr", "ContactEmail", "CustomerEmail"],
    "Address": ["Address", "Addr", "Street"],
    "City": ["City", "Town"],
    "State": ["State", "Province"],
    "ZipCode": ["Zip", "PostalCode", "ZipCode"],
    "BeneficiaryName": ["Beneficiary", "BeneficiaryName", "RecipientName"],
    "BeneficiaryEmail": ["BeneficiaryEmail", "RecipientEmail"],
    "CoverageAmount": ["Coverage", "CoverageAmount", "InsuredAmount"],
    "PolicyType": ["PolicyType", "Type", "PlanType"],
    "StartDate": ["StartDate", "EffectiveDate"],
    "EndDate": ["EndDate", "ExpiryDate"],
    "PremiumAmount": ["Premium", "PremiumAmount", "PaymentAmount"],
}


def auto_detect_format(input_text: str) -> Tuple[Any, str]:
    """
    Auto-detects the format of the input text.
    Returns a tuple (parsed_data, format_type) where format_type can be 'json', 'xml', 'csv', or 'text'.
    """
    # Attempt to parse as JSON
    try:
        data = json.loads(input_text)
        return data, "json"
    except json.JSONDecodeError:
        pass

    # Attempt to parse as XML
    try:
        root = ET.fromstring(input_text)
        # Convert XML to dict (simple conversion)
        data = {child.tag: child.text for child in root}
        return data, "xml"
    except ET.ParseError:
        pass

    # Attempt to parse as CSV
    try:
        csv_reader = csv.DictReader(io.StringIO(input_text))
        data = list(csv_reader)
        if data:
            return data, "csv"
    except Exception:
        pass

    # Fallback: assume plain text (natural language)
    return input_text, "text"


def get_standard_field(field_name: str) -> str:
    """
    Returns the standardized field name based on the mapping dictionary.
    If no mapping is found, returns the original field name.
    """
    for standard, synonyms in FIELD_MAPPINGS.items():
        if field_name in synonyms:
            return standard
    return field_name


def normalize_columns(data: Union[dict, list]) -> Union[dict, list]:
    """
    Normalizes column names in the parsed data.
    Handles both dictionary (single record) and list (e.g., CSV rows) formats.
    """
    if isinstance(data, dict):
        normalized = {}
        for key, value in data.items():
            normalized[get_standard_field(key)] = value
        return normalized
    elif isinstance(data, list):
        normalized_list = []
        for row in data:
            normalized_row = {}
            for key, value in row.items():
                normalized_row[get_standard_field(key)] = value
            normalized_list.append(normalized_row)
        return normalized_list
    else:
        return data


def enhance_user_intent(text: str) -> dict:
    """
    Simulates the extraction of a structured schema from natural language input using an LLM.
    Replace this simulation with an actual call to an LLM (e.g., via AWS Bedrock) when ready.
    """
    simulated_schema = {
        "fields": ["FullName", "CustomerEmail", "PhoneNumber"],
        "constraints": {
            "FullName": {"type": "string"},
            "CustomerEmail": {"type": "string", "format": "email"},
            "PhoneNumber": {"type": "string"},
        },
        "output_format": "CSV",
    }
    return simulated_schema


def load_base_template() -> dict:
    template_path = os.path.join(
        os.path.dirname(__file__), "..", "templates", "life_insurance_template.json"
    )
    with open(template_path, "r") as f:
        base_template = json.load(f)
    return base_template


def merge_with_template(parsed_schema: Union[dict, list], base_template: dict) -> dict:
    merged_template = base_template.copy()
    base_fields = merged_template.get("fields", {})

    # If parsed_schema is a dict (single record)
    if isinstance(parsed_schema, dict):
        for key, value in parsed_schema.items():
            standard_key = get_standard_field(key)
            if standard_key not in base_fields:
                inferred_type = (
                    "number" if isinstance(value, (int, float)) else "string"
                )
                base_fields[standard_key] = {
                    "datatype": inferred_type,
                    "description": "User provided field",
                }
    # If parsed_schema is a list (e.g., multiple rows from CSV)
    elif isinstance(parsed_schema, list) and len(parsed_schema) > 0:
        for row in parsed_schema:
            for key, value in row.items():
                standard_key = get_standard_field(key)
                if standard_key not in base_fields:
                    inferred_type = (
                        "number" if isinstance(value, (int, float)) else "string"
                    )
                    base_fields[standard_key] = {
                        "datatype": inferred_type,
                        "description": "User provided field",
                    }
    merged_template["fields"] = base_fields
    return merged_template


def preprocess_input(request: GenerateRequest) -> str:
    """
    Processes the user input (request) to build a dynamic prompt.
    Steps:
      1. Auto-detect input format.
      2. Normalize column names if applicable.
      3. Enhance user intent using simulated LLM extraction when input is plain text.
    Finally, it constructs the final prompt string.
    """
    input_text = request.prompt
    parsed_data, format_type = auto_detect_format(input_text)

    if format_type == "text":
        # For plain language input, simulate an LLM extracting a schema.
        user_schema = enhance_user_intent(parsed_data)
    else:
        # For structured input, normalize column names.
        user_schema = normalize_columns(parsed_data)

    base_template = load_base_template()
    merged_schema = merge_with_template(user_schema, base_template)

    # Construct the final prompt string.
    final_prompt = (
        f"Schema: {merged_schema}. "
        f"Generate {request.volume} records in {request.input_format} format."
    )
    return final_prompt


# For debugging, you can test these functions independently.
if __name__ == "__main__":
    # Example inputs:
    json_input = '{"FirstName": "John", "EmailAddr": "john@example.com"}'
    xml_input = "<root><FirstName>John</FirstName><EmailAddr>john@example.com</EmailAddr></root>"
    csv_input = "FirstName,EmailAddr\nJohn,john@example.com"
    plain_text_input = "Please generate customer records with first name, email address, and phone number."

    class DummyRequest:
        def __init__(self, prompt, input_format, volume):
            self.prompt = prompt
            self.input_format = input_format
            self.volume = volume

    # Testing each scenario:
    for inp in [json_input, xml_input, csv_input, plain_text_input]:
        dummy_request = DummyRequest(prompt=inp, input_format="CSV", volume=1000)
        logger.info("Final Prompt:", preprocess_input(dummy_request))
