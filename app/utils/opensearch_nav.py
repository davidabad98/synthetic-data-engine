from opensearchpy import OpenSearch

# --- CONFIGURE THIS FOR YOUR ENVIRONMENT ---
OPENSEARCH_ENDPOINT = "https://search-genai-schema-search-d63w6q24vjesd7sqzhzdxbt2ay.us-east-1.es.amazonaws.com"
OPENSEARCH_USER = "GenAI"
OPENSEARCH_PASS = "GenAI@2025"
INDEX_NAME = "schema_search"
# -------------------------------------------

def connect():
    """Creates an OpenSearch client connection."""
    return OpenSearch(
        hosts=[OPENSEARCH_ENDPOINT],
        http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS)
    )

def list_doc_ids_and_names():
    """Lists document IDs and schema_name values from the index."""
    client = connect()
    query = {"query": {"match_all": {}}}
    
    response = client.search(index=INDEX_NAME, body=query, scroll='2m', size=100)
    scroll_id = response.get('_scroll_id')
    hits = response['hits']['hits']

    if not hits:
        print("No documents found.")
        return

    print(f"\n📄 Found {response['hits']['total']['value']} documents:\n")

    while hits:
        for doc in hits:
            doc_id = doc['_id']
            schema_name = doc['_source'].get('schema_name', 'N/A')
            print(f"🆔 ID: {doc_id}, Name: {schema_name}")

        response = client.scroll(scroll_id=scroll_id, scroll='2m')
        hits = response['hits']['hits']

def delete_document_by_id(doc_id):
    client = connect()
    try:
        delete_response = client.delete(index=INDEX_NAME, id=doc_id)
        print(f"✅ Deleted document with ID: {doc_id} — {delete_response['result']}")
    except Exception as e:
        print(f"⚠️ Error deleting document with ID: {doc_id} - {e}")

if __name__ == "__main__":
    #List documents
    list_doc_ids_and_names()

    # Delete documents (Uncomment and add schema names if needed)

    # doc_id_to_delete = "3w8XCJYBuXHnAaSvuTE_"
    # delete_document_by_id(doc_id_to_delete)
