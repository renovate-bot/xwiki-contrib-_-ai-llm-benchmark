import json
import os
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Split input JSON file into individual question files organized by task.')
parser.add_argument('--input-file', required=True, help='Path to the input JSON file')
parser.add_argument('--output-dir', required=True, help='Directory to store the organized question files')
args = parser.parse_args()

# Read the input JSON file
with open(args.input_file, 'r') as file:
    data = json.load(file)

# Create the output directory if it doesn't exist
os.makedirs(args.output_dir, exist_ok=True)

# Iterate over each task in the JSON data
for task_name, items in data['tasks'].items():
    # Create a directory for each task
    task_dir = os.path.join(args.output_dir, task_name)
    os.makedirs(task_dir, exist_ok=True)

    # Iterate over each item in the task
    for item in items:
        question_id = item['id']
        
        # Create a new JSON file for each item if it doesn't already exist
        output_file = os.path.join(task_dir, f"{question_id}.json")
        if not os.path.exists(output_file):
            with open(output_file, 'w') as file:
                json.dump(item, file, indent=2)

print(f"Individual question files created successfully in {args.output_dir}, organized by task.")
