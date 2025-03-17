# app/utils/template_loader.py
import json
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def load_single_template(template_name, templates_dir=TEMPLATES_DIR):
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


def load_template_mappings():
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
                print(f"Warning: Skipping invalid JSON file {filename}")
    return templates
