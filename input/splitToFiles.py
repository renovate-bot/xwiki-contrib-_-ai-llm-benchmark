import json
import os

# Read the input JSON file
with open("input/input.json", "r") as file:
    data = json.load(file)

# Create a directory to store the individual question files
dir = "input/questions"
os.makedirs(dir, exist_ok=True)

# Iterate over each question in the JSON data
for question in data["questions"]:
    question_id = question["id"]
    
    # Create a new JSON file for the question
    output_file = os.path.join(dir, f"{question_id}.json")
    with open(output_file, "w") as file:
        json.dump(question, file, indent=2)

print("Individual question files created successfully.")