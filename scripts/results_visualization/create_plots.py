import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

# Function to read JSON files
def read_json_files(directory):
    data = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):
                with open(os.path.join(root, filename), 'r') as f:
                    data.append(json.load(f))
    return data

# Function to generate bar charts
def generate_bar_chart(data, task, criterion, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Criterion', y='Score', hue='Model', data=df)
    plt.title(f'{task.capitalize()} Task Scores Comparison ({criterion})')
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to generate grouped bar charts for all criteria
def generate_grouped_bar_chart(data, task, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Criterion', y='Score', hue='Model', data=df)
    plt.title(f'{task.capitalize()} Task Scores Comparison')
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to generate box plots
def generate_box_plot(data, task, criterion, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Criterion', y='Score', hue='Model', data=df)
    plt.title(f'{task.capitalize()} Task Score Distribution ({criterion})')
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to load configuration
def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

# Function to process evaluation results and generate visualizations
def process_evaluation_results(config, results_dir, output_dir):
    tasks = config['tasks']
    criteria = {
        'summarization': ['score'],
        'text_generation': ['score'],
        'RAG-qa': ['AnswerRelevancy', 'Faithfulness', 'ContextualPrecision', 'ContextualRecall']
    }

    for task in tasks:
        task_name = task['task']
        task_dir = os.path.join(results_dir, task_name)
        bar_data = []

        for model in os.listdir(task_dir):
            model_dir = os.path.join(task_dir, model)
            data = read_json_files(model_dir)

            # Prepare data for bar charts
            for item in data:
                for criterion in criteria[task_name]:
                    if item.get('score_breakdown') and criterion in item['score_breakdown']:
                        bar_data.append({
                            'Model': model,
                            'Criterion': criterion,
                            'Score': item['score_breakdown'][criterion]
                        })
                    else:
                        bar_data.append({
                            'Model': model,
                            'Criterion': criterion,
                            'Score': item.get('average_score', item.get('score', 0)) # Default to 0 if 'score' is not present
                        })

        # Generate bar charts for each criterion
        for criterion in criteria[task_name]:
            filtered_data = [d for d in bar_data if d['Criterion'] == criterion]
            generate_bar_chart(filtered_data, task_name, criterion, output_dir, f'{task_name}_{criterion}_bar_chart.png')
            generate_box_plot(filtered_data, task_name, criterion, output_dir, f'{task_name}_{criterion}_box_plot.png')

        # Generate grouped bar chart for all criteria
        generate_grouped_bar_chart(bar_data, task_name, output_dir, f'{task_name}_grouped_bar_chart.png')

# Function to generate average power consumption bar chart
def generate_average_power_chart(data, output_dir, file_name):
    df = pd.DataFrame(data)
    print("Data for average power chart:", df)  # Debug print statement
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Model', y='Average Power Consumption', data=df)
    plt.title('Average Power Consumption by Model')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to generate average power consumption grouped bar chart
def generate_average_power_grouped_chart(data, output_dir, file_name):
    df = pd.DataFrame(data)
    print("Data for average power grouped chart:", df)  # Debug print statement
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Model', y='power_consumption', hue='Task', data=df)
    plt.title('Average Power Consumption by Model and Task')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to generate detailed power consumption charts
def generate_detailed_power_charts(data, output_dir):
    df = pd.DataFrame(data)
    print("Data for detailed power charts:", df)  # Debug print statement
    metrics = ['power_per_input_token', 'power_per_output_token', 'power_per_total_token']
    for metric in metrics:
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Model', y=metric, hue='Task', data=df)
        plt.title(f'Average {metric.replace("_", " ").capitalize()} by Model and Task')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(output_dir, f'average_{metric}_grouped_chart.png'))
        plt.close()

# Function to process average power consumption data and generate visualizations
def process_average_power_data(results_dir, output_dir):
    average_power_file = os.path.join(results_dir, 'average_power_consumption.json')
    if os.path.exists(average_power_file):
        with open(average_power_file, 'r') as f:
            average_power_data = json.load(f)

        model_data = []
        task_data = []
        for model, data in average_power_data.items():
            model_data.append({
                'Model': model,
                'Average Power Consumption': data['model_average']
            })
            for task, power_data in data['task_averages'].items():
                task_data.append({
                    'Model': model,
                    'Task': task,
                    'power_consumption': power_data['power_consumption'],
                    'power_per_input_token': power_data['power_per_input_token'],
                    'power_per_output_token': power_data['power_per_output_token'],
                    'power_per_total_token': power_data['power_per_total_token']
                })

        generate_average_power_chart(model_data, output_dir, 'average_power_consumption_chart.png')
        generate_average_power_grouped_chart(task_data, output_dir, 'average_power_consumption_grouped_chart.png')
        generate_detailed_power_charts(task_data, output_dir)
    else:
        print(f"Average power consumption data file not found: {average_power_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate plots from evaluation results.")
    parser.add_argument('--config', required=True, help='Path to the configuration file.')
    parser.add_argument('--results_dir', required=True, help='Path to the evaluation results directory.')
    parser.add_argument('--output_dir', required=True, help='Path to the output directory for plots.')

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Load configuration and run the processing function
    config = load_config(args.config)
    process_evaluation_results(config, args.results_dir, args.output_dir)

    # Process average power consumption data and generate visualizations
    process_average_power_data(args.results_dir, args.output_dir)
