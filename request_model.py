import boto3
import json
from io import StringIO
import pandas as pd
import re
import requests
import config  # Contains: REGION_NAME, GROQ_API_KEY, GROQ_URL

class requestModel:
    def __init__(self):
        self.region_name = config.REGION_NAME
        self.GROQ_API_KEY = config.GROQ_API_KEY
        self.groq_url = config.GROQ_URL

    def send_request_titan(self, prompt):
        # Initialize AWS session and Bedrock client
        session = boto3.Session(profile_name="GenAI_Permission-688567268018")
        bedrock_client = session.client("bedrock-runtime", region_name=self.region_name)

        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 4000,
                "temperature": 0.7,
                "topP": 0.9
            }
        }

        response = bedrock_client.invoke_model(
            modelId="meta.llama3-1-70b-instruct-v1:0",
            body=json.dumps(payload)
        )

        response_body = json.loads(response["body"].read())
        output_text = response_body['results'][0]['outputText']

        print("=== Raw Titan Output ===")
        print(output_text)
        print("========================")

        # Try to extract CSV from markdown block or fallback CSV pattern
        csv_data_match = re.search(r'```tabular-data-csv\s*(.*?)```', output_text, re.DOTALL)
        if not csv_data_match:
            csv_data_match = re.search(r'(?i)(Name.*?,.*?\n(?:.*?,.*?\n*)+)', output_text)

        if csv_data_match:
            csv_data = csv_data_match.group(1).strip()
        else:
            raise ValueError("❌ No CSV data found in the provided text.\nFull Output:\n" + output_text)

        df = pd.read_csv(StringIO(csv_data))
        print(f"✅ {len(df)} rows of data generated using Titan")

        return df

    def send_request_groq(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(self.groq_url, json=data, headers=headers)
        response_json = response.json()
        print(response_json)
        csv_data = response_json["choices"][0]["message"]["content"]

        df = pd.read_csv(StringIO(csv_data))
        print(f"✅ {len(df)} rows of data generated using Groq")

        print("=== Raw Groq Model Response ===")
        print(csv_data)
        print("===============================")

        return df
