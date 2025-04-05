import json
import boto3
from opensearchpy import OpenSearch
import urllib.parse

# --- CONFIGURE ---
S3_CLIENT = boto3.client("s3")
OPENSEARCH_CLIENT = OpenSearch(
    hosts=["https://search-genai-schema-search-d63w6q24vjesd7sqzhzdxbt2ay.us-east-1.es.amazonaws.com"],
    http_auth=("GenAI", "GenAI@2025")
)
INDEX_NAME = "schema_search"
# ------------------

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        if not key.endswith(".json"):
            print(f"Skipping non-JSON file: {key}")
            continue

        try:
            response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
            file_content = response["Body"].read().decode("utf-8")
            schema_json = json.loads(file_content)

            description = schema_json.get("description", "No description provided.")
            schema_data_str = json.dumps(schema_json)
            schema_name = key.split("/")[-1].replace(".json", "")

            doc = {
                "schema_name": schema_name,
                "description": description,
                "schema_data": schema_data_str
            }

            resp = OPENSEARCH_CLIENT.index(index=INDEX_NAME, body=doc)
            print(f"Indexed schema '{schema_name}' with ID: {resp['_id']}")

        except Exception as e:
            print(f"Error processing file {key} from bucket {bucket}: {e}")

    return {"statusCode": 200, "body": "Done"}
