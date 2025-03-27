import json
import logging
import re
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CsvParser:
    """Class to parse and process JSON data from LLM responses"""

    @staticmethod
    def parse_csv_response(raw_response: str):
        """
        Process raw LLM response and extract valid JSON data
        Args:
            raw_response: Raw string response from LLM
        Returns:
            List of parsed JSON dictionaries
        """
        try:
            # Extract the CSV data from the output text
            csv_data_match = re.search(
                r"```tabular-data-csv\s*(.*)\s*```", raw_response, re.DOTALL
            )
            if csv_data_match:
                csv_data = csv_data_match.group(1)
            else:
                raise ValueError("No CSV data found in the provided text.")

            return csv_data

        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Parsing failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
