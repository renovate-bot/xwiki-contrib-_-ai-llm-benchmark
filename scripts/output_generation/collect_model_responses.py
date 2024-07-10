import os
import sys
import json
import argparse
import time
import subprocess
import threading

# Add the project's root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.models_connections.waise_model import WaiseModel

def parse_arguments():
    parser = argparse.ArgumentParser(description='Collect data from the WAISE API.')
    parser.add_argument('--input-dir', required=True, help='Directory containing input task files')
    parser.add_argument('--output-dir', required=True, help='Directory to store the output results')
    parser.add_argument('--request-template', default='config.json', help='Path to the request template file')
    return parser.parse_args()

def send_request_to_model(model, temperature, stream, question):
    waise_model = WaiseModel(model=model, temperature=temperature, stream=stream, verbose=True)
    response = waise_model.invoke(question)
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

def get_gpu_power_usage():
    try:
        output = subprocess.check_output(['nvidia-smi', '--query-gpu=power.draw', '--format=csv,nounits,noheader'])
        power_usage = float(output.decode('utf-8').strip())
        return power_usage
    except (FileNotFoundError, subprocess.CalledProcessError):
        return 'N/A'
    
def measure_power_consumption(model, temperature, stream, question, baseline_power):
    power_readings = []
    stop_event = threading.Event()
    
    power_thread = threading.Thread(target=collect_power_readings, args=(power_readings, stop_event))
    power_thread.start()
    
    start_time = time.time()
    response = send_request_to_model(model, temperature, stream, question)
    end_time = time.time()
    
    stop_event.set()
    power_thread.join()
    
    duration = end_time - start_time
    
    if power_readings:
        avg_power = sum(power_readings) / len(power_readings)
        avg_power_draw = avg_power - baseline_power  # Average power draw above baseline
        energy_consumption = avg_power_draw * duration  # Energy in Joules
    else:
        avg_power_draw = 'N/A'
        energy_consumption = 'N/A'

    return response, avg_power_draw, energy_consumption



def collect_power_readings(power_readings, stop_event):
    while not stop_event.is_set():
        power_usage = get_gpu_power_usage()
        if isinstance(power_usage, float):
            power_readings.append(power_usage)
        time.sleep(0.1)  # Adjust the interval as needed

def process_request(task_name, question_data, settings, question_file, baseline_power, measure_power):
    question_id = question_data['id']
    if task_name == 'RAG-qa' or task_name == 'text_generation':
        question = question_data['prompt']
        expected_answer = question_data['expected_answer']
    elif task_name == 'summarization':
        data_path = question_data['data_path']
        abs_data_path = os.path.abspath(os.path.join(os.path.dirname(question_file), '..', '..', data_path))
        content = load_data(abs_data_path)["content"]
        question = f"Please summarize the following text:\n\n{content}"
        expected_answer = None
    else:
        raise ValueError(f"Unknown task: {task_name}")

    model = settings['model']
    temperature = settings['temperature']
    stream = settings['stream']

    if measure_power:
        response, avg_power_draw, energy_consumption = measure_power_consumption(model, temperature, stream, question, baseline_power)
    else:
        response = send_request_to_model(model, temperature, stream, question)
        avg_power_draw = 'N/A'
        energy_consumption = 'N/A'

    answer_content = response['choices'][0]['message']['content']
    sources = response['choices'][0]['message']['context']
    usage = response.get('usage', {})

    # Calculate energy per token metrics
    energy_per_input_token = 'N/A'
    energy_per_output_token = 'N/A'
    energy_per_total_token = 'N/A'

    if usage and energy_consumption != 'N/A':
        energy_per_input_token = energy_consumption / usage['prompt_tokens'] if usage.get('prompt_tokens', 0) > 0 else 'N/A'
        energy_per_output_token = energy_consumption / usage['completion_tokens'] if usage.get('completion_tokens', 0) > 0 else 'N/A'
        energy_per_total_token = energy_consumption / usage['total_tokens'] if usage.get('total_tokens', 0) > 0 else 'N/A'

    return {
        'id': question_id,
        'prompt': question,
        'expected_answer': expected_answer,
        'ai_answer': answer_content,
        'sources': sources,
        'usage': usage,
        'average_power_draw': f"{avg_power_draw:.4f} W" if avg_power_draw != 'N/A' else 'N/A',
        'energy_consumption': f"{energy_consumption:.4f} J" if energy_consumption != 'N/A' else 'N/A',
        'energy_per_input_token': f"{energy_per_input_token:.4f} J/token" if energy_per_input_token != 'N/A' else 'N/A',
        'energy_per_output_token': f"{energy_per_output_token:.4f} J/token" if energy_per_output_token != 'N/A' else 'N/A',
        'energy_per_total_token': f"{energy_per_total_token:.4f} J/token" if energy_per_total_token != 'N/A' else 'N/A'
    }

def process_tasks(input_dir, output_dir, request_template, baseline_power):
    for task in request_template['tasks']:
        task_name = task['task']
        settings = task['settings']
        model_name = settings['model']
        measure_power = task.get('power_measurement', False)
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
                result = process_request(task_name, question_data, settings, question_file, baseline_power, measure_power)
                save_result(output_dir, model_name, task_name, question_id, result)
    print(f"All requests processed. Results stored in {output_dir}.")

def main():
    args = parse_arguments()
    request_template = load_data(args.request_template)

    # Measure baseline power usage
    print("Measuring baseline power usage...")
    baseline_power_readings = []
    start_time = time.time()
    while time.time() - start_time < 5:  # Measure baseline power for 5 seconds
        power_usage = get_gpu_power_usage()
        if isinstance(power_usage, float):
            baseline_power_readings.append(power_usage)
        time.sleep(0.1)  # Adjust the interval as needed
    baseline_power = sum(baseline_power_readings) / len(baseline_power_readings)
    print(f"Baseline power usage: {baseline_power} W")
    print("Gathering responses...")
    process_tasks(args.input_dir, args.output_dir, request_template, baseline_power)
    os.makedirs("snakeout/collected", exist_ok=True)

if __name__ == '__main__':
    main()
