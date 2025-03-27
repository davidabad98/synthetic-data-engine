import json
from opensearchpy import OpenSearch
from request_model import requestModel
import utility
import config

# --- CONFIGURE THIS FOR YOUR ENVIRONMENT ---
OPENSEARCH_ENDPOINT = "https://search-genai-schema-search-d63w6q24vjesd7sqzhzdxbt2ay.us-east-1.es.amazonaws.com"
OPENSEARCH_USER = "GenAI"
OPENSEARCH_PASS = "GenAI@2025"
INDEX_NAME = "schema_search"
# --------------------------------------------

def get_best_matching_schema(user_prompt):
    client = OpenSearch(
        hosts=[OPENSEARCH_ENDPOINT],
        http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS)
    )

    query = {
        "size": 1,
        "query": {
            "multi_match": {
                "query": user_prompt,
                "fields": [
                    "template_name^2",
                    "description",
                    "mappings"
                ]
            }
        }
    }

    response = client.search(index=INDEX_NAME, body=query)
    hits = response["hits"]["hits"]

    if not hits:
        return None, None

    top_hit = hits[0]["_source"]
    schema_json_str = top_hit["schema_data"]
    schema_json = json.loads(schema_json_str)
    return schema_json, top_hit.get("template_name")

def main():
    user_prompt = input("Enter your prompt: ")
    schema, schema_name = get_best_matching_schema(user_prompt)

    if not schema:
        print("No matching schema found.")
        return

    print(f"Best matching schema: {schema_name}")

    # Create prompt for model
    model_prompt = f"Generate  synthetic data using the following schema and give it in CSV format Enclose the data entirely within backticks for easy extraction Do not provide explanations, code samples, or additional text. Only provide the data.:\n{json.dumps(schema)}\n\nPrompt: {user_prompt}"

    model_client = requestModel()
    response = model_client.send_request_titan(model_prompt)
    destination_uri = utility.save_dataframe_to_s3(response, bucket_name = config.S3_OUTPUT_BUCKET, prefix = config.S3_OUTPUT_FOLDER)
    print("\n--- Model Response ---")
    print(destination_uri)
    print(response)

if __name__ == "__main__":
    main()
