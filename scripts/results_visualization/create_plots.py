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
                            'Score': item.get('average_score', item.get('score', 0))  # Default to 0 if 'score' is not present
                        })

        # Generate bar charts for each criterion
        for criterion in criteria[task_name]:
            filtered_data = [d for d in bar_data if d['Criterion'] == criterion]
            generate_bar_chart(filtered_data, task_name, criterion, output_dir, f'{task_name}_{criterion}_bar_chart.png')
            generate_box_plot(filtered_data, task_name, criterion, output_dir, f'{task_name}_{criterion}_box_plot.png')

        # Generate grouped bar chart for all criteria
        generate_grouped_bar_chart(bar_data, task_name, output_dir, f'{task_name}_grouped_bar_chart.png')

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
