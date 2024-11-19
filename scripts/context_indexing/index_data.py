from dotenv import load_dotenv
import os
import requests
import json
import html
import argparse

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Index data using the WAISE API.')
parser.add_argument('--collections-dir', required=True, help='Directory containing collection JSON files')
parser.add_argument('--documents-dir', required=True, help='Directory containing document JSON and text files')
args = parser.parse_args()

# Resolve the relative paths to absolute paths
collections_dir = os.path.abspath(args.collections_dir)
documents_dir = os.path.abspath(args.documents_dir)

# Load environment variables from .env file
load_dotenv()

# Waise server connection information
wiki_name = os.getenv('WIKI_NAME')
base_url = os.getenv('BASE_URL').format(wikiName=wiki_name)

# Authentication credentials
username = os.getenv('WAISE_USERNAME')
password = os.getenv('WAISE_PASSWORD')
auth = (username, password)

def get_valid_collections(collections_dir):
    valid_collections = set()
    for collection_file in os.listdir(collections_dir):
        if collection_file.endswith('.json'):
            with open(os.path.join(collections_dir, collection_file), 'r') as file:
                collection_data = json.load(file)
                valid_collections.add(collection_data['id'])
    return valid_collections

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

def put_document(document_json_file, document_content_file, collection):
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
    document_data['collection'] = collection
    url = f'{base_url}/collections/{document_data["collection"]}/documents/{document_data["id"]}?media=json'
    response = requests.put(url, json=document_data, auth=auth)
    try:
        return response.json()
    except ValueError as e:
        error_message = f"Failed to decode JSON from response: Status code {response.status_code}, Response body: {response.text}"
        raise ValueError(error_message) from e

def index_data(collections_dir, documents_dir):
    valid_collections = get_valid_collections(collections_dir)

    # Index collections
    for collection_file in os.listdir(collections_dir):
        if collection_file.endswith('.json'):
            collection_json_file = os.path.join(collections_dir, collection_file)
            put_collection(collection_json_file)
            print(f"Indexing collection: {collection_json_file}")

    # Index documents
    for document_file in os.listdir(documents_dir):
        if document_file.endswith('.json'):
            document_json_file = os.path.join(documents_dir, document_file)
            with open(document_json_file, 'r') as file:
                document_data = json.load(file)

            if isinstance(document_data['collection'], list):
                collections = document_data['collection']
            else:
                collections = [document_data['collection']]

            # Filter collections by valid collections.
            collections = [collection for collection in collections if collection in valid_collections]

            if collections:
                document_name = os.path.splitext(document_file)[0]
                document_txt_file = os.path.join(documents_dir, f"{document_name}.txt")
                for collection in collections:
                    put_document(document_json_file, document_txt_file, collection)
                print(f"Indexing document: {document_json_file}")
                if not os.path.exists(document_txt_file):
                    print(f"Warning: Corresponding .txt file not found for {document_file}: using json content field instead")
            else:
                print(f"Skipping document {document_file}: not in any valid collection")

    print("Indexing completed.")


if __name__ == '__main__':
    ####
    # Populate collections using the index API
    index_data(collections_dir, documents_dir)
    ####
    # Uncomment the function below to remove indexed evaluation data
    # delete_all_collections(collections_dir)
