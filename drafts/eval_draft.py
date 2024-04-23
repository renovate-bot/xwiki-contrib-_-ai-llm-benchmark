import random
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from unittest.mock import Mock

# Define dummy data sources
dummy_sources = [
    {"id": 1, "text": "Python is a high-level programming language."},
    {"id": 2, "text": "Python is commonly used for data analysis and machine learning."},
    {"id": 3, "text": "Python has a large ecosystem of libraries and frameworks."}
]

# Define dummy queries and expected results
dummy_queries = [
    {"query": "What is Python?", "expected_source_ids": [1]},
    {"query": "What is Python used for?", "expected_source_ids": [2]},
    {"query": "Does Python have many libraries?", "expected_source_ids": [3]}
]

# Mock the search engine's retrieval and response generation functions
def mock_retrieve_sources(query):
    # Randomly select 1-2 sources for each query
    return random.sample(dummy_sources, random.randint(1, 2))

def mock_generate_response(query, sources):
    # Concatenate the text from the retrieved sources
    response_text = " ".join([source["text"] for source in sources])
    return {"query": query, "response_text": response_text, "source_ids": [source["id"] for source in sources]}

# Evaluation metrics
def calculate_metrics(actual_source_ids, expected_source_ids):
    # Get the unique source IDs from both lists
    all_source_ids = list(set(actual_source_ids) | set(expected_source_ids))
    
    # Convert the source IDs into binary vectors
    actual_binary = [int(source_id in actual_source_ids) for source_id in all_source_ids]
    expected_binary = [int(source_id in expected_source_ids) for source_id in all_source_ids]
    
    precision = precision_score(expected_binary, actual_binary)
    recall = recall_score(expected_binary, actual_binary)
    f1 = f1_score(expected_binary, actual_binary)
    return precision, recall, f1


# Main evaluation loop
def evaluate_waise():
    results = []
    
    for query_data in dummy_queries:
        query = query_data["query"]
        expected_source_ids = query_data["expected_source_ids"]
        
        # Mock the retrieval and response generation process
        retrieved_sources = mock_retrieve_sources(query)
        response = mock_generate_response(query, retrieved_sources)
        actual_source_ids = response["source_ids"]
        
        # Calculate evaluation metrics
        precision, recall, f1 = calculate_metrics(actual_source_ids, expected_source_ids)
        
        results.append({
            "Query": query,
            "Expected Sources": expected_source_ids,
            "Actual Sources": actual_source_ids,
            "Precision": precision,
            "Recall": recall,
            "F1 Score": f1
        })
    
    # Create a DataFrame with the evaluation results
    results_df = pd.DataFrame(results)
    return results_df

# Run the evaluation
evaluation_results = evaluate_waise()

# Print the evaluation results
print("Evaluation Results:")
print(evaluation_results)