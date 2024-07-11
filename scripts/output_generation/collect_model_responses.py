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
    question, expected_answer = prepare_question(task_name, question_data, question_file)

    model = settings['model']
    temperature = settings['temperature']
    stream = settings['stream']

    response, avg_power_draw, energy_consumption = measure_model_performance(
        model, temperature, stream, question, baseline_power, measure_power
    )

    result = process_response(response, question_id, question, expected_answer)
    result.update(calculate_energy_metrics(energy_consumption, response['usage'], avg_power_draw))

    return result

def prepare_question(task_name, question_data, question_file):
    if task_name in ['RAG-qa', 'text_generation']:
        return question_data['prompt'], question_data['expected_answer']
    elif task_name == 'summarization':
        content = load_data(os.path.abspath(os.path.join(os.path.dirname(question_file), '..', '..', question_data['data_path'])))["content"]
        return f"Please summarize the following text:\n\n{content}", None
    else:
        raise ValueError(f"Unknown task: {task_name}")

def measure_model_performance(model, temperature, stream, question, baseline_power, measure_power):
    if measure_power:
        return measure_power_consumption(model, temperature, stream, question, baseline_power)
    else:
        return send_request_to_model(model, temperature, stream, question), 'N/A', 'N/A'

def process_response(response, question_id, question, expected_answer):
    return {
        'id': question_id,
        'prompt': question,
        'expected_answer': expected_answer,
        'ai_answer': response['choices'][0]['message']['content'],
        'sources': response['choices'][0]['message']['context'],
        'usage': response.get('usage', {})
    }

def calculate_energy_metrics(energy_consumption, usage, avg_power_draw):
    if energy_consumption == 'N/A':
        return {
            'average_power_draw': 'N/A',
            'energy_consumption': 'N/A',
            'energy_per_input_token': 'N/A',
            'energy_per_output_token': 'N/A',
            'energy_per_total_token': 'N/A'
        }

    input_tokens = usage['prompt_tokens']
    output_tokens = usage['completion_tokens']
    total_tokens = usage['total_tokens']

    input_weight = 1
    output_weight = 2.5

    weighted_input_tokens = input_tokens * input_weight
    weighted_output_tokens = output_tokens * output_weight
    total_weighted_tokens = weighted_input_tokens + weighted_output_tokens

    input_energy = (weighted_input_tokens / total_weighted_tokens) * energy_consumption
    output_energy = (weighted_output_tokens / total_weighted_tokens) * energy_consumption

    return {
        'average_power_draw': f"{avg_power_draw:.4f} W",
        'energy_consumption': f"{energy_consumption:.4f} J",
        'energy_per_input_token': f"{(input_energy / input_tokens):.4f} J/token",
        'energy_per_output_token': f"{(output_energy / output_tokens):.4f} J/token",
        'energy_per_total_token': f"{(energy_consumption / total_tokens):.4f} J/token"
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
