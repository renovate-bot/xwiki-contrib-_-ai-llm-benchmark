import os
import json
import argparse
import requests
from dotenv import load_dotenv

def load_environment_variables():
    load_dotenv()
    return os.getenv('WIKI_NAME'), os.getenv('BASE_URL'), os.getenv('WAISE_USERNAME'), os.getenv('WAISE_PASSWORD')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Collect data from the WAISE API.')
    parser.add_argument('--input-dir', required=True, help='Directory containing input task files')
    parser.add_argument('--output-dir', required=True, help='Directory to store the output results')
    parser.add_argument('--request-template', default='config.json', help='Path to the request template file')
    return parser.parse_args()

def send_request_to_model(base_url, auth, model, temperature, stream, question):
    url = f'{base_url}/v1/chat/completions'
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "temperature": temperature,
        "stream": stream,
        "messages": [{"role": "user", "content": question}]
    }
    response = requests.post(url, headers=headers, json=data, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
    return response

def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_result(output_dir, model_name, task_name, question_id, result):
    model_dir = os.path.join(output_dir, model_name)
    task_dir = os.path.join(model_dir, 'tasks', task_name)
    os.makedirs(task_dir, exist_ok=True)
    output_file = os.path.join(task_dir, f"{question_id}.json")
    with open(output_file, 'w') as file:
        json.dump(result, file, indent=2)

def process_request(task_name, question_data, settings, base_url, auth, question_file):
    question_id = question_data['id']
    if task_name == 'RAG-qa':
        question = question_data['prompt']
        expected_answer = question_data['expected_answer']
    elif task_name == 'summarization':
        data_path = question_data['data_path']
        # Construct the absolute path based on the relative path
        abs_data_path = os.path.abspath(os.path.join(os.path.dirname(question_file), '..', '..', data_path))
        content = load_data(abs_data_path)["content"]
        question = f"Please summarize the following text:\n\n{content}"
        expected_answer = None
    elif task_name == 'text_generation':
        question = question_data['prompt']
        expected_answer = question_data['expected_answer']
    else:
        raise ValueError(f"Unknown task: {task_name}")

    model = settings['model']
    temperature = settings['temperature']
    stream = settings['stream']
    response = send_request_to_model(base_url, auth, model, temperature, stream, question)
    answer_content = response.json()['choices'][0]['message']['content']
    sources = response.json()['choices'][0]['message']['context']
    return {
        'id': question_id,
        'prompt': question,
        'expected_answer': expected_answer,
        'ai_answer': answer_content,
        'sources': sources
    }

def process_tasks(input_dir, output_dir, request_template, base_url, auth):
    for task in request_template['tasks']:
        task_name = task['task']
        settings = task['settings']
        model_name = settings['model']
        task_input_dir = os.path.join(input_dir, task_name)
        filenames = os.listdir(task_input_dir)
        for filename in filenames:
            if filename.endswith(".json"):
                question_file = os.path.join(task_input_dir, filename)
                question_data = load_data(question_file)
                question_id = question_data['id']
                output_file = os.path.join(output_dir, model_name, 'tasks', task_name, f"{question_id}.json")
                if os.path.exists(output_file):
                    print(f"Skipping question {question_id} as it already exists.")
                    continue
                result = process_request(task_name, question_data, settings, base_url, auth, question_file)
                save_result(output_dir, model_name, task_name, question_id, result)
    print(f"All requests processed. Results stored in {output_dir}.")

def main():
    args = parse_arguments()
    wiki_name, base_url_template, username, password = load_environment_variables()
    base_url = base_url_template.format(wikiName=wiki_name)
    auth = (username, password)
    request_template = load_data(args.request_template)
    process_tasks(args.input_dir, args.output_dir, request_template, base_url, auth)
    os.makedirs("snakeout/collected", exist_ok=True)

if __name__ == '__main__':
    main()
