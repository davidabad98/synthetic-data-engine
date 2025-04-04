# app/config/config.py

# Turn on OpenSearch
OPEN_SEARCH = False
OPENSEARCH_ENDPOINT = "https://search-genai-schema-search-d63w6q24vjesd7sqzhzdxbt2ay.us-east-1.es.amazonaws.com"
OPENSEARCH_USER = "GenAI"
OPENSEARCH_PASS = "GenAI@2025"
INDEX_NAME = "schema_search"

# Server mode can be either "local" or "aws"
SERVER_MODE = "local"

# main_template (1) OR main (2)
SERVER_FLOW = 2

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
# LLM_BEDROCK_MODEL_ID = "amazon.titan-text-express-v1"
LLM_BEDROCK_MODEL_ID = "anthropic.claude-v2:1"
LLM_BEDROCK_ENDPOINT = "https://bedrock.endpoint.url"

# AWS KEYS
REGION_NAME = "us-east-1"
AWS_PROFILE = "DavidAbad"
S3_BUCKET_NAME = "synthetic-data-templates"
S3_TEMPLATE_PATH = "schemas/"  # Folder in S3 bucket

# S3 buckets info
S3_INPUT_FILEPATH = "s3://genaiinput-dataset/CustomerClaimsDataset.csv"
S3_OUTPUT_BUCKET = "genaioutput-dataset"
S3_OUTPUT_FOLDER = "output/"

# GROQ configuration for local deployment
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_ID = "llama3-8b-8192"

# FLOW 1 FLAGS
SUPPORTED_FORMATS = ["CSV", "XML", "JSON", "TEXT"]
DEFAULT_FORMAT = "CSV"
DEFAULT_RECORD_COUNT = 5

# FLOW 2 FLAGS
N_SAMPLES = 3
GENERATED_ROWS = 10
SAMPLE_DATA_FILE = "CustomerClaimsDataset.csv"
