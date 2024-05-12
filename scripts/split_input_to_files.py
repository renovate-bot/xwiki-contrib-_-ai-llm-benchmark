import json
import os
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Split input JSON file into individual question files.')
parser.add_argument('--input-file', required=True, help='Path to the input JSON file')
parser.add_argument('--output-dir', required=True, help='Directory to store the individual question files')
args = parser.parse_args()

# Read the input JSON file
with open(args.input_file, 'r') as file:
    data = json.load(file)

# Create the output directory if it doesn't exist
os.makedirs(args.output_dir, exist_ok=True)

# Iterate over each question in the JSON data
for question in data['questions']:
    question_id = question['id']
    
    # Create a new JSON file for the question
    output_file = os.path.join(args.output_dir, f"{question_id}.json")
    with open(output_file, 'w') as file:
        json.dump(question, file, indent=2)

print(f"Individual question files created successfully in {args.output_dir}.")
