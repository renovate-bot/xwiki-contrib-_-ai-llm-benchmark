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

def load_request_template():
    with open('request.json', 'r') as file:
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
    x_sources = response.headers.get('X-Sources', '[]')

    try:
        sources_json = json.loads(x_sources)
    except (json.JSONDecodeError, KeyError):
        sources_json = []

    result = {
        # 'model': model,
        # 'temperature': temperature,
        'id': question_id,
        'question': question,
        'expected_answer': expected_answer,
        'ai_answer': answer_content,
        'sources': sources_json
    }

    return result

def process_requests(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    request_template = load_request_template()

    ## This is just to process the files in order but os.listdir(input_dir) would also work
    filenames = sorted(os.listdir(input_dir), key=lambda x: int(x.split('.')[0]))

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

    print("All requests processed.")


# define evaluation metrics 

# calculate evaluation scores

# produce plots

# compile report

if __name__ == '__main__':
    ####
    # Paths
    input_dir = 'input/questions'
    output_file = 'output'
    ####
    # Data
    ####


    ####
    # Send a request to a model
    process_requests(input_dir, output_file)