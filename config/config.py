# app/config/config.py

# Server mode can be either "local" or "aws"
SERVER_MODE = "cloud"

# List of domain-specific filler phrases to remove
FILLER_PHRASES = [
    "synthetic data",
    "synth data",
    "mock data",
    "test data",
    "dummy data",
    "simulated data",
    "fabricated data",
    "artificial data",
    "generated data",
    "sample data",
    "synthetic records",
    "mock records",
    "test records",
    "dummy records",
    "simulated records",
    "fabricated records",
    "artificial records",
    "generated records",
    "fake data",
    "fake records",
    "data for testing",
    "data for simulation",
    "data for mockup",
    "data for example",
    "synthetic information",
    "mock information",
    "test information",
    "dummy information",
    "simulated information",
    "fabricated information",
    "artificial information",
    "generated information",
    "policy",
    "data",
    "records",
]

# LLM configuration for local deployment
LLM_LOCAL_URL = "http://10.111.30.94:1234/v1/completions"

# LLM configuration for AWS Bedrock (example values)
LLM_BEDROCK_MODEL_ID = "anthropic.claude-v2"
LLM_BEDROCK_ENDPOINT = "https://bedrock.endpoint.url"

# AWS KEYS
AWS_PROFILE = "DavidAbad"
S3_BUCKET_NAME = "synthetic-data-templates"
S3_TEMPLATE_PATH = "schemas/"  # Folder in S3 bucket

# Titan configuration for local deployment
PROFILE_NAME = "rizvan"
REGION_NAME = "us-east-1"
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_ID = "mixtral-8x7b-32768"
