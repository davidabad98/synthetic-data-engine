import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class JsonParser:
    """Class to parse and process JSON data from LLM responses"""

    def __init__(self, schema: Optional[Dict] = None):
        self.schema = schema
        self.parsed_data = []

    def parse_response(self, raw_response: str) -> List[Dict]:
        """
        Process raw LLM response and extract valid JSON data
        Args:
            raw_response: Raw string response from LLM
        Returns:
            List of parsed JSON dictionaries
        """
        try:
            # Extract content between <<REPLY>> tags
            reply_content = self._extract_reply_content(raw_response)

            # Extract JSON objects
            json_objects = self._extract_json_objects(reply_content)

            # Validate against schema if provided
            if self.schema:
                self._validate_schema(json_objects)

            self.parsed_data = json_objects
            return json_objects

        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Parsing failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    @staticmethod
    def _extract_reply_content(raw_response: str) -> str:
        """Extract content between <<REPLY>> tags"""
        reply_pattern = r"<<REPLY>>(.*?)\[/REPLY\]"
        match = re.search(reply_pattern, raw_response, re.DOTALL)

        if not match:
            raise ValueError("No <<REPLY>> block found in response")

        return match.group(1).strip()

    @staticmethod
    def _extract_json_objects(content: str) -> List[Dict]:
        """Extract multiple JSON objects from string content"""
        json_objects = []
        # Pattern to find JSON objects (including nested)
        json_pattern = r"\{.*?\}(?=\s*\{|\s*$)"

        matches = re.finditer(json_pattern, content, re.DOTALL)

        for match in matches:
            try:
                json_str = match.group()
                # Clean potential trailing commas
                json_str = re.sub(r",\s*}", "}", json_str)
                json_obj = json.loads(json_str)
                json_objects.append(json_obj)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON found: {str(e)}")
                continue

        if not json_objects:
            raise ValueError("No valid JSON objects found in reply content")

        return json_objects

    def _validate_schema(self, data: List[Dict]):
        """Validate data against provided JSON schema"""
        if not self.schema:
            return

        # Implement your schema validation logic here
        # Example using jsonschema:
        # from jsonschema import validate
        # for item in data:
        #     validate(instance=item, schema=self.schema)
        logger.info("Schema validation passed")

    def save_to_file(self, file_path: Path, indent: int = 2):
        """
        Save parsed data to JSON file
        Args:
            file_path: Path object for output file
            indent: JSON indentation level
        """
        if not self.parsed_data:
            raise ValueError("No data to save. Call parse_response() first")

        try:
            with open(file_path, "w") as f:
                json.dump(self.parsed_data, f, indent=indent)
            logger.info(f"Successfully saved data to {file_path}")
        except IOError as e:
            logger.error(f"File save failed: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # Your raw response string here
    with open("./data/llm_response.txt", "r") as f:
        sample_response = f.read()

    # Initialize parser
    parser = JsonParser()

    try:
        parsed_data = parser.parse_response(sample_response)
        parser.save_to_file(Path("data.json"))

        logger.info(f"Successfully parsed {len(parsed_data)} records")
        logger.info("Sample record:", json.dumps(parsed_data[0], indent=2))

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
