# app/utils/template_loader.py
import json
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def load_template(template_name, templates_dir=TEMPLATES_DIR):
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
