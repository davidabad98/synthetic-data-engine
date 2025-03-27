import json
import logging
import re
from io import StringIO

import boto3
import pandas as pd
import requests

from config.config import (
    GROQ_API_KEY,
    GROQ_MODEL_ID,
    GROQ_URL,
    LLM_BEDROCK_MODEL_ID,
    PROFILE_NAME,
    REGION_NAME,
)

logger = logging.getLogger(__name__)


class RequestModel:
    def __init__(self):
        self.profile_name = PROFILE_NAME
        self.region_name = REGION_NAME
        self.GROQ_API_KEY = GROQ_API_KEY
        self.groq_url = GROQ_URL

    def send_request_titan(self, prompt):
        # Initialize AWS Session with IAM Identity Center (SSO) profile
        session = boto3.Session(profile_name=self.profile_name)

        # Create Bedrock client
        bedrock_client = session.client("bedrock-runtime", region_name=self.region_name)

        # Define the request payload
        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 4000,
                "temperature": 0.7,
                "topP": 0.9,
            },
        }

        # Invoke the Titan model
        response = bedrock_client.invoke_model(
            modelId=LLM_BEDROCK_MODEL_ID, body=json.dumps(payload)
        )

        with response["body"] as stream:
            response_body = json.loads(stream.read())

        # Extract the output text
        output_text = response_body["results"][0]["outputText"]

        # Extract the CSV data from the output text
        csv_data_match = re.search(
            r"```tabular-data-csv\s*(.*)\s*```", output_text, re.DOTALL
        )
        if csv_data_match:
            csv_data = csv_data_match.group(1)
        else:
            raise ValueError("No CSV data found in the provided text.")

        # Load the CSV data into a Pandas DataFrame
        return self._parse_csv_response(csv_data, "titan")

    def send_request_groq(self, prompt):
        # Define the API endpoint and headers
        API_KEY = self.GROQ_API_KEY
        url = self.groq_url

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": GROQ_MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
        }
        # Send the request to the Groq API
        response = requests.post(url, json=data, headers=headers)

        # Extracting the message content
        response_json = response.json()
        csv_data = response_json["choices"][0]["message"]["content"]

        # Convert the CSV data into a pandas DataFrame
        return self._parse_csv_response(csv_data, "groq")

    def _parse_csv_response(self, csv_data: str, source: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(StringIO(csv_data))
            logger.info(f"{len(df)} rows generated using {source}")
            return df
        except pd.errors.ParserError as e:
            logger.error(f"CSV parsing failed: {str(e)}")
            raise
