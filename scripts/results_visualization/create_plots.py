import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

criteria = {
    'summarization': ['Alignment', 'Coverage'],
    'text_generation': ['score'],
    'RAG-qa': ['AnswerRelevancy', 'Faithfulness', 'ContextualPrecision', 'ContextualRecall']
}

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
    sns.barplot(x='Model', y='Score', data=df[df['Criterion'] == criterion])
    plt.title(f'{task.capitalize()} Task Scores Comparison ({criterion})')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to generate grouped bar charts for all criteria
def generate_grouped_bar_chart(data, task, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Model', y='Score', hue='Criterion', data=df)
    plt.title(f'{task.capitalize()} Task Scores Comparison')
    plt.xticks(rotation=45)
    plt.legend(title='Criterion', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to generate box plots
def generate_box_plot(data, task, criterion, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Model', y='Score', data=df[df['Criterion'] == criterion])
    plt.title(f'{task.capitalize()} Task Score Distribution ({criterion})')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to load configuration
def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

# Function to process evaluation results and generate visualizations
def process_evaluation_results(config, results_dir, output_dir):
    tasks = config['tasks']

    for task in tasks:
        task_name = task['task']
        task_dir = os.path.join(results_dir, task_name)
        bar_data = []

        for model in os.listdir(task_dir):
            model_dir = os.path.join(task_dir, model)
            data = read_json_files(model_dir)

            # Prepare data for bar charts
            for item in data:
                if task_name == 'RAG-qa':
                    for criterion, score in item['individual_scores'].items():
                        bar_data.append({
                            'Model': model,
                            'Criterion': criterion,
                            'Score': score
                        })
                elif task_name == 'summarization':
                    for criterion, score in item['score_breakdown'].items():
                        bar_data.append({
                            'Model': model,
                            'Criterion': criterion,
                            'Score': score
                        })
                else:  # text_generation
                    bar_data.append({
                        'Model': model,
                        'Criterion': 'score',
                        'Score': item['score']
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
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Model', y='Average Power Consumption', data=df)
    plt.title('Average Power Consumption by Model')
    plt.ylabel('Average Power Consumption (W)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()


# Function to generate average power consumption grouped bar chart
def generate_average_power_grouped_chart(data, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Model', y='power_consumption', hue='Task', data=df)
    plt.title('Average Energy Consumption by Model and Task')
    plt.ylabel('Energy Consumption (J)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()


# Function to generate detailed power consumption charts
def generate_detailed_power_charts(data, output_dir):
    df = pd.DataFrame(data)
    metrics = {
        'power_per_input_token': 'J/token',
        'power_per_output_token': 'J/token',
        'power_per_total_token': 'J/token'
    }
    for metric, unit in metrics.items():
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Model', y=metric, hue='Task', data=df)
        plt.title(f'Average {metric.replace("_", " ").capitalize()} by Model and Task')
        plt.ylabel(f'{metric.replace("_", " ").capitalize()} ({unit})')
        plt.xticks(rotation=45)
        plt.tight_layout()
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
                'Average Power Consumption': data['model_average_power']
            })
            for task, power_data in data['task_averages'].items():
                task_data.append({
                    'Model': model,
                    'Task': task,
                    'power_consumption': power_data['energy_consumption'],
                    'power_per_input_token': power_data['energy_per_input_token'],
                    'power_per_output_token': power_data['energy_per_output_token'],
                    'power_per_total_token': power_data['energy_per_total_token']
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
