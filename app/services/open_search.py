import json
import logging

from opensearchpy import OpenSearch

import config
from config.config import (
    INDEX_NAME,
    OPENSEARCH_ENDPOINT,
    OPENSEARCH_PASS,
    OPENSEARCH_USER,
)

logger = logging.getLogger(__name__)


def get_best_matching_schema(user_prompt):
    client = OpenSearch(
        hosts=[OPENSEARCH_ENDPOINT], http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS)
    )

    query = {
        "size": 1,
        "query": {
            "multi_match": {
                "query": user_prompt,
                "fields": ["template_name^2", "description", "mappings"],
            }
        },
    }

    response = client.search(index=INDEX_NAME, body=query)
    hits = response["hits"]["hits"]

    if not hits:
        return None, None

    top_hit = hits[0]["_source"]
    schema_json_str = top_hit["schema_data"]
    schema_json = json.loads(schema_json_str)
    schema_name = top_hit.get("template_name")
    logger.info(f"OpenSearch best matching schema: {schema_name}")

    return schema_json, schema_name
