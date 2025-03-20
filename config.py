# app/config/config.py

# Server mode can be either "local" or "aws"
SERVER_MODE = "local"

# LLM configuration for local deployment
LLM_LOCAL_URL = "http://10.111.30.94:1234/v1/completions"

# LLM configuration for AWS Bedrock (example values)
LLM_BEDROCK_MODEL_ID = "anthropic.claude-v2"
LLM_BEDROCK_ENDPOINT = "https://bedrock.endpoint.url"

# Titan configuration for local deployment
TITAN_PROFILE_NAME_RIZVAN = 'rizvan'
REGION_NAME = 'us-east-1'
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# S3 buckets info
S3_INPUT_FILEPATH = 's3://genaiinput-dataset/CustomerClaimsDataset.csv'
S3_OUTPUT_BUCKET = 'genaioutput-dataset'
S3_OUTPUT_FOLDER = 'output/'