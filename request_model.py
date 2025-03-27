import boto3
import json
from io import StringIO
import pandas as pd
import re
import requests
import config #TITAN_PROFILE_NAME_RIZVAN, REGION_NAME, GROQ_API_KEY, GROQ_URL
class requestModel:
    def __init__(self):
        #self.titan_profile_name = config.TITAN_PROFILE_NAME_RIZVAN
        self.region_name = config.REGION_NAME
        self.GROQ_API_KEY = config.GROQ_API_KEY
        self.groq_url = config.GROQ_URL

    def send_request_titan(self,prompt):
        # Initialize AWS Session with IAM Identity Center (SSO) profile
        session = boto3.Session()
        
        # Create Bedrock client
        bedrock_client = session.client("bedrock-runtime", region_name=self.region_name)
        
        # Define the request payload
        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 4000,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        # Invoke the Titan model
        response = bedrock_client.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            body=json.dumps(payload)
        )
        
        # Print the response
        response_body = json.loads(response["body"].read())

            # Extract the output text
        output_text = response_body['results'][0]['outputText']

        # Extract the CSV data from the output text
        csv_data_match = re.search(r'```tabular-data-csv\s*(.*)\s*```', output_text, re.DOTALL)
        if csv_data_match:
            csv_data = csv_data_match.group(1)
        else:
            raise ValueError("No CSV data found in the provided text.")
        
        # Load the CSV data into a Pandas DataFrame
        df = pd.read_csv(StringIO(csv_data))
        print("{} rows of data generated using titan".format(len(df)))

        return df

    def send_request_groq(self, prompt):
        # Define the API endpoint and headers
        API_KEY = self.GROQ_API_KEY
        url = self.groq_url

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}]
        }
        # Send the request to the Groq API
        response = requests.post(url, json=data, headers=headers)

        # Extracting the message content
        response_json = response.json()
        print(response_json)
        csv_data = response_json["choices"][0]["message"]["content"]

        # Convert the CSV data into a pandas DataFrame
        df = pd.read_csv(StringIO(csv_data))
        print("{} rows of data generated using groq".format(len(df)))
        return df
if __name__ == "__main__":
    rm  = requestModel()
    prompt = "Generate 10 rows of data for the following columns: Customer ID, First Name, Last Name, Email, Phone Number, Address, City, State, Zip Code, Country, Product ID, Product Name, Quantity, Price, Order Date, Shipping Date, Delivery Date, Payment Method, Payment Status, Order Status, Tracking Number, Notes."
    df = rm.send_request_groq(prompt)