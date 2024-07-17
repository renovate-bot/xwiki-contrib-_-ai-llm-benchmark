import os
import json
import argparse
from collections import defaultdict

def calculate_average_power(evaluation_dir, output_dir):
    model_power_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Traverse the evaluation directory to collect power consumption data
    for root, dirs, files in os.walk(evaluation_dir):
        if 'tasks' in dirs:
            task_dirs = [os.path.join(root, 'tasks', task_dir) for task_dir in os.listdir(os.path.join(root, 'tasks'))]
            for task_dir in task_dirs:
                for file in os.listdir(task_dir):
                    if file.endswith('.json'):
                        file_path = os.path.join(task_dir, file)
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            model_name = root.split(os.sep)[-1]
                            task_name = task_dir.split(os.sep)[-1]
                            
                            # Extract energy metrics
                            average_power_draw = data.get('average_power_draw')
                            energy_consumption = data.get('energy_consumption')
                            energy_per_input_token = data.get('energy_per_input_token')
                            energy_per_output_token = data.get('energy_per_output_token')
                            energy_per_total_token = data.get('energy_per_total_token')
                            
                            # Only process valid numerical data
                            if all(metric is not None for metric in [average_power_draw, energy_consumption, energy_per_input_token, energy_per_output_token, energy_per_total_token]):
                                model_power_data[model_name][task_name]['average_power_draw'].append(average_power_draw)
                                model_power_data[model_name][task_name]['energy_consumption'].append(energy_consumption)
                                model_power_data[model_name][task_name]['energy_per_input_token'].append(energy_per_input_token)
                                model_power_data[model_name][task_name]['energy_per_output_token'].append(energy_per_output_token)
                                model_power_data[model_name][task_name]['energy_per_total_token'].append(energy_per_total_token)

    # Calculate average power consumption
    average_power_results = {}
    for model_name, tasks in model_power_data.items():
        model_total_power = 0
        model_total_count = 0
        task_averages = {}
        for task_name, power_data in tasks.items():
            task_average = {
                'average_power_draw': sum(power_data['average_power_draw']) / len(power_data['average_power_draw']),
                'energy_consumption': sum(power_data['energy_consumption']) / len(power_data['energy_consumption']),
                'energy_per_input_token': sum(power_data['energy_per_input_token']) / len(power_data['energy_per_input_token']),
                'energy_per_output_token': sum(power_data['energy_per_output_token']) / len(power_data['energy_per_output_token']),
                'energy_per_total_token': sum(power_data['energy_per_total_token']) / len(power_data['energy_per_total_token'])
            }
            task_averages[task_name] = task_average
            model_total_power += sum(power_data['energy_consumption'])
            model_total_count += len(power_data['energy_consumption'])
        
        model_average_power = model_total_power / model_total_count if model_total_count > 0 else None
        average_power_results[model_name] = {
            'model_average_power': model_average_power,
            'task_averages': task_averages
        }

    # Save the results
    os.makedirs(output_dir, exist_ok=True)
    result_file = os.path.join(output_dir, 'average_power_consumption.json')
    with open(result_file, 'w') as f:
        json.dump(average_power_results, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Calculate average power consumption.')
    parser.add_argument('--evaluation-dir', required=True, help='Directory containing the evaluation results')
    parser.add_argument('--output-dir', required=True, help='Directory to store the average power consumption results')
    args = parser.parse_args()

    calculate_average_power(args.evaluation_dir, args.output_dir)
    os.makedirs("snakeout/average_power", exist_ok=True)

if __name__ == '__main__':
    main()
