from dotenv import load_dotenv
import os
import requests
import json
import html

# Load environment variables from .env file
load_dotenv()

# Waise server connection information
wiki_name = os.getenv('WIKI_NAME')
base_url = os.getenv('BASE_URL').format(wikiName=wiki_name)

# Authentication credentials
username = os.getenv('WAISE_USERNAME')
password = os.getenv('WAISE_PASSWORD')
auth = (username, password)

# Populate collections using the index API.
def delete_collection(collection_name):
    """Delete a specific collection."""
    url = f'{base_url}/collections/{collection_name}?media=json'
    response = requests.delete(url, auth=auth)
    return response.status_code

def delete_all_collections(collections_dir):
    # Iterate through all the files in the collections directory
    for collection_file in os.listdir(collections_dir):
        if collection_file.endswith('.json'):
            with open(os.path.join(collections_dir, collection_file), 'r') as file:
                collection_data = json.load(file)
            collection_id = collection_data['id']
            print(f"Deleting collection: {collection_id}")
            delete_collection(collection_id)

def put_collection(collection_json_file):
    """Create or update a collection."""
    with open(collection_json_file, 'r') as file:
        collection_data = json.load(file)
    collection_name = collection_data['id']
    url = f'{base_url}/collections/{collection_name}?media=json'
    response = requests.put(url, json=collection_data, auth=auth)
    try:
        return response.json()
    except ValueError as e:
        error_message = f"Failed to decode JSON from response: Status code {response.status_code}, Response body: {response.text}"
        raise ValueError(error_message) from e

def put_document(document_json_file, document_content_file):
    """Create or update a document in a collection."""
    with open(document_json_file, 'r') as file:
        document_data = json.load(file)
    try:
        with open(document_content_file, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        content = document_data.get('content', '')
    content = html.escape(content)
    document_data['content'] = content
    url = f'{base_url}/collections/{document_data["collection"]}/documents/{document_data["id"]}?media=json'
    response = requests.put(url, json=document_data, auth=auth)
    try:
        return response.json()
    except ValueError as e:
        error_message = f"Failed to decode JSON from response: Status code {response.status_code}, Response body: {response.text}"
        raise ValueError(error_message) from e

def index_data(collections_dir, documents_dir):
    # Iterate through all the files in the collections directory
    for collection_file in os.listdir(collections_dir):
        if collection_file.endswith('.json'):
            collection_json_file = os.path.join(collections_dir, collection_file)
            put_collection(collection_json_file)
            print(f"Indexing collection: {collection_json_file}")

    # Iterate through all the .json files in the documents directory
    for document_file in os.listdir(documents_dir):
        if document_file.endswith('.json'):
            document_json_file = os.path.join(documents_dir, document_file)
            document_name = os.path.splitext(document_file)[0]
            document_txt_file = os.path.join(documents_dir, f"{document_name}.txt")
            put_document(document_json_file, document_txt_file)
            print(f"Indexing document: {document_json_file}")
            if not os.path.exists(document_txt_file):
                print(f"Warning: Corresponding .txt file not found for {document_file}: using json content field instead")


if __name__ == '__main__':
    ####
    # Paths
    collection_dir = 'context_data/collections'
    document_dir = 'context_data/documents'
    ####
    # Populate collections using the index API
    index_data(collection_dir, document_dir)
    ####
    # Uncomment the function below to remove indexed evaluation data
    # delete_all_collections(collectio_dir)