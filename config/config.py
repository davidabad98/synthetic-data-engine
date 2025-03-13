# app/config/config.py

# Server mode can be either "local" or "aws"
SERVER_MODE = "local"

# LLM configuration for local deployment
LLM_LOCAL_URL = "http://10.111.30.94:1234/v1/completions"

# LLM configuration for AWS Bedrock (example values)
LLM_BEDROCK_MODEL_ID = "anthropic.claude-v2"
LLM_BEDROCK_ENDPOINT = "https://bedrock.endpoint.url"
