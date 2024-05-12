from dotenv import load_dotenv
import os
import requests
import json
import html
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Collect data from the WAISE API.')
parser.add_argument('--input-dir', required=True, help='Directory containing input question files')
parser.add_argument('--output-dir', required=True, help='Directory to store the output results')
parser.add_argument('--request-template', default='request.json', help='Path to the request template file')
args = parser.parse_args()

# Load environment variables from .env file
load_dotenv()

# Waise server connection information
wiki_name = os.getenv('WIKI_NAME')
base_url = os.getenv('BASE_URL').format(wikiName=wiki_name)

# Authentication credentials
username = os.getenv('WAISE_USERNAME')
password = os.getenv('WAISE_PASSWORD')
auth = (username, password)

# Input data in json format (the questions to be run against waise) and collect responses
def send_request_to_model(model, temperature, stream, messages):
    url = f'{base_url}/v1/chat/completions'
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "temperature": temperature,
        "stream": stream,
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            return response
        except json.JSONDecodeError:
            error_message = f"Failed to decode JSON from response: Status code {response.status_code}, Response body: {response.text}"
            raise Exception(error_message)
    else:
        error_message = f"Request failed with status code {response.status_code}: {response.text}"
        raise Exception(error_message)

def load_question_data(question_file):
    with open(question_file, 'r') as file:
        question_data = json.load(file)
    return question_data

def load_request_template(request_template_file):
    with open(request_template_file, 'r') as file:
        request_template = json.load(file)
    return request_template

def save_result(output_dir, question_id, result):
    output_file = os.path.join(output_dir, f"{question_id}.json")
    with open(output_file, 'w') as file:
        json.dump(result, file, indent=2)

def process_request(question_data, request_template):
    question_id = question_data['id']
    question = question_data['question']
    expected_answer = question_data['expected_answer']

    model = request_template['model']
    temperature = request_template['temperature']
    stream = request_template['stream']
    messages = request_template['messages']

    messages[0]['content'] = question

    response = send_request_to_model(model, temperature, stream, messages)

    answer_content = response.json()['choices'][0]['message']['content']
    x_sources = response.json()['choices'][0]['message']['context']

    result = {
        # 'model': model,
        # 'temperature': temperature,
        'id': question_id,
        'question': question,
        'expected_answer': expected_answer,
        'ai_answer': answer_content,
        'sources': x_sources
    }

    return result

def process_requests(input_dir, output_dir, request_template_file):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    request_template = load_request_template(request_template_file)

    filenames = os.listdir(input_dir)
    filenames.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else float('inf'))

    for filename in filenames:
        if filename.endswith(".json"):
            question_file = os.path.join(input_dir, filename)
            question_data = load_question_data(question_file)
            question_id = question_data['id']

            output_file = os.path.join(output_dir, f"{question_id}.json")
            if os.path.exists(output_file):
                print(f"Skipping question {question_id} as it already exists.")
                continue

            result = process_request(question_data, request_template)
            save_result(output_dir, question_id, result)

    print(f"All requests processed. Results stored in {output_dir}.")

if __name__ == '__main__':
    process_requests(args.input_dir, args.output_dir, args.request_template)
