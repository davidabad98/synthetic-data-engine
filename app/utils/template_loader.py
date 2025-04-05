# app/utils/template_loader.py
import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

from config.config import (
    AWS_PROFILE,
    OPEN_SEARCH,
    S3_BUCKET_NAME,
    S3_TEMPLATE_PATH,
    SERVER_MODE,
)

logger = logging.getLogger(__name__)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def load_single_template(template_name):
    """
    Load single template from local files or an S3 bucket based on SERVER_MODE.
    """
    if SERVER_MODE == "local":
        return _get_template_from_local(template_name)
    else:
        return _get_template_from_s3(template_name)


def _get_template_from_local(template_name, templates_dir=TEMPLATES_DIR):
    """
    Loads a JSON template file given its name.
    Returns the JSON content as a Python dictionary or None if not found.
    """
    template_name += ".json"
    template_path = os.path.join(templates_dir, template_name)
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _get_template_from_s3(template_name: str):
    """
    Retrieves a specific JSON template from S3 by name.

    Args:
        template_name (str): Name of the template without extension

    Returns:
        dict: Parsed JSON template content or None if not found/invalid

    Example:
        >>> get_template_from_s3("tax_free_savings")
        {'template_name': 'tax_free_savings', 'mappings': [...]}
    """
    # Explicitly set the AWS profile
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3_client = session.client("s3")
    object_key = f"{S3_TEMPLATE_PATH}{template_name}.json"

    try:
        # Get template object from S3
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=object_key)

        # Read and parse content
        file_content = response["Body"].read().decode("utf-8")
        return json.loads(file_content)

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            logger.warning(f"Template '{template_name}' not found in S3")
        else:
            logger.error(f"S3 ClientError retrieving '{template_name}': {str(e)}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in template '{template_name}'")
        return None
    except UnicodeDecodeError:
        logger.error(f"Encoding error in template '{template_name}'")
        return None
    except Exception as e:
        logger.exception(
            f"Unexpected error loading template '{template_name}': {str(e)}"
        )

    return None


def load_template_mappings():
    """
    Load template mappings from local files or an S3 bucket based on SERVER_MODE.
    """
    if OPEN_SEARCH:
        return "NOT_FOUND"
    if SERVER_MODE == "local":
        return _load_template_mappings_from_local()
    else:
        return _load_template_mappings_from_s3()


def _load_template_mappings_from_local():
    """
    Dynamically loads all templates from the /templates directory
    and constructs the TEMPLATE_CANDIDATES dictionary where:
    - Key = template_name
    - Value = mappings
    """
    templates = {}
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(TEMPLATES_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    template_name = data.get("template_name")
                    mappings = data.get("mappings", [])
                    if template_name and mappings:
                        templates[template_name] = mappings
            except json.JSONDecodeError:
                logger.error(f"Warning: Skipping invalid JSON file {filename}")
    return templates


def _load_template_mappings_from_s3():
    """
    Loads all JSON templates from the 'schema/' directory in the S3 bucket.
    Constructs the TEMPLATE_CANDIDATES dictionary where:
    - Key = template_name
    - Value = mappings
    """
    # Explicitly set the AWS profile
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3_client = session.client("s3")
    templates = {}

    try:
        # List all objects under the /schema/ folder
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME, Prefix=S3_TEMPLATE_PATH
        )

        if "Contents" not in response:
            logger.info("Warning: No templates found in S3 bucket.")
            return templates

        # Iterate through all files in the schema folder
        for obj in response["Contents"]:
            file_key = obj["Key"]

            # Ensure we're only processing JSON files
            if not file_key.endswith(".json"):
                continue

            # Fetch and read the JSON file from S3
            s3_object = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=file_key)
            file_content = s3_object["Body"].read().decode("utf-8")

            try:
                data = json.loads(file_content)
                template_name = data.get("template_name")
                mappings = data.get("mappings", [])

                if template_name and mappings:
                    templates[template_name] = mappings
            except json.JSONDecodeError:
                logger.error(f"Warning: Skipping invalid JSON file {file_key}")

    except Exception as e:
        logger.error(f"Error fetching templates from S3: {str(e)}")

    return templates
