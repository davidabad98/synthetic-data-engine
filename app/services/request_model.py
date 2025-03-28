import json
import logging
import re
from io import StringIO

import boto3
import pandas as pd
import requests

from app.services.csv_parser import CsvParser
from config.config import (
    AWS_PROFILE,
    GROQ_API_KEY,
    GROQ_MODEL_ID,
    GROQ_URL,
    LLM_BEDROCK_MODEL_ID,
    REGION_NAME,
)

logger = logging.getLogger(__name__)


class RequestModel:
    def __init__(self):
        self.AWS_PROFILE = AWS_PROFILE
        self.region_name = REGION_NAME
        self.GROQ_API_KEY = GROQ_API_KEY
        self.groq_url = GROQ_URL

    def send_request_bedrock(
        self, prompt, max_tokens=4000, temperature=0.7, top_p=0.9, top_k=250
    ):
        # Initialize AWS Session with IAM Identity Center (SSO) profile
        session = boto3.Session(profile_name=self.AWS_PROFILE)

        # Create Bedrock client
        bedrock_client = session.client("bedrock-runtime", region_name=self.region_name)

        # Define the request payload

        # Antrhopic
        payload = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "stop_sequences": ["\n\nHuman:"],
            "anthropic_version": "bedrock-2023-05-31",
        }

        # payload = {
        #     "inputText": prompt,
        #     "textGenerationConfig": {
        #         "maxTokenCount": 4000,
        #         "temperature": 0.7,
        #         "topP": 0.9,
        #     },
        # }

        # Invoke the Titan model
        response = bedrock_client.invoke_model(
            modelId=LLM_BEDROCK_MODEL_ID, body=json.dumps(payload)
        )

        with response["body"] as stream:
            response_body = json.loads(stream.read())

        # Extract the output text
        # output_text = response_body["results"][0]["outputText"]

        # Extract the generated response from Claude
        output_text = response_body.get("completion", "").strip()

        # Extract the CSV data from the output text
        csv_data = CsvParser.parse_csv_response(output_text)

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

        # Extract the CSV data from the output text
        csv_data = CsvParser.parse_csv_response(csv_data)

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
