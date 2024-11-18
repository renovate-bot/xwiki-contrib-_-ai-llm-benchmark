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
    sorted_models = df[df['Criterion'] == criterion].groupby('Model')['Score'].mean().sort_values().index.to_list()
    sns.barplot(x='Model', y='Score', data=df[df['Criterion'] == criterion], order=sorted_models)
    plt.title(f'{task.capitalize()} Task Scores Comparison ({criterion})')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

# Function to generate grouped bar charts for all criteria
def generate_grouped_bar_chart(data, task, output_dir, file_name):
    df = pd.DataFrame(data)
    
    # Calculate the average score for each model
    model_avg_scores = df.groupby('Model')['Score'].mean().sort_values(ascending=True)
    
    # Sort the models based on their average scores
    sorted_models = model_avg_scores.index.tolist()
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Model', y='Score', hue='Criterion', data=df, order=sorted_models)
    plt.title(f'{task.capitalize()} Task Scores Comparison')
    plt.xticks(rotation=45, ha='right')
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
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

def generate_overall_score_box_plot(data, output_dir, file_name):
    df = pd.DataFrame(data)
    sorted_models = df.groupby('Model')['overall_score'].median().sort_values().index.to_list()
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Model', y='overall_score', data=df, order=sorted_models)
    plt.title('RAG-qa Task Overall Score Distribution')
    plt.ylabel('Overall Score')
    plt.xticks(rotation=45, ha='right')
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
    criteria = {
        'summarization': ['Alignment', 'Coverage'],
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

        # Generate overall score box plot for RAG-qa task
        if task_name == 'RAG-qa':
            overall_scores = []
            for model in os.listdir(task_dir):
                model_dir = os.path.join(task_dir, model)
                data = read_json_files(model_dir)
                for item in data:
                    overall_scores.append({
                        'Model': model,
                        'overall_score': item['overall_score']
                    })
            generate_overall_score_box_plot(overall_scores, output_dir, f'{task_name}_overall_score_box_plot.png')


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
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

def generate_average_power_draw_chart(data, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Model', y='average_power_draw', data=df)
    plt.title('Average Power Draw by Model')
    plt.ylabel('Average Power Draw (W)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()

def generate_model_average_power_chart(data, output_dir, file_name):
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Model', y='Model Average Power', data=df)
    plt.title('Model Average Power Consumption')
    plt.ylabel('Model Average Power (J)')
    plt.xticks(rotation=45, ha='right')
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
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()


# Function to generate detailed power consumption charts
def generate_detailed_power_charts(data, output_dir):
    df = pd.DataFrame(data)
    metrics = [
        ('average_power_draw', 'W'),
        ('energy_consumption', 'J'),
        ('energy_per_input_token', 'J/token'),
        ('energy_per_output_token', 'J/token'),
        ('energy_per_total_token', 'J/token')
    ]
    
    for metric, unit in metrics:
        if metric in df.columns:
            plt.figure(figsize=(12, 8))
            sns.barplot(x='Model', y=metric, hue='Task', data=df)
            plt.title(f'Average {metric.replace("_", " ").capitalize()} by Model and Task')
            plt.ylabel(f'{metric.replace("_", " ").capitalize()} ({unit})')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'average_{metric}_grouped_chart.png'))
            plt.close()
        else:
            print(f"Warning: Metric '{metric}' not found in data")


# Function to process average power consumption data and generate visualizations
def process_average_power_data(results_dir, output_dir):
    average_power_file = os.path.join(results_dir, 'average_power_consumption.json')
    
    if not os.path.exists(average_power_file):
        print(f"Average power consumption data file not found: {average_power_file}")
        return

    try:
        with open(average_power_file, 'r') as f:
            average_power_data = json.load(f)

        power_draw_data = []
        model_power_data = []
        for model, data in average_power_data.items():
            model_power_data.append({
                'Model': model,
                'Model Average Power': data['model_average_power']
            })
            for task, power_data in data['task_averages'].items():
                power_draw_data.append({
                    'Model': model,
                    'Task': task,
                    'average_power_draw': power_data['average_power_draw'],
                    'energy_consumption': power_data['energy_consumption'],
                    'energy_per_input_token': power_data['energy_per_input_token'],
                    'energy_per_output_token': power_data['energy_per_output_token'],
                    'energy_per_total_token': power_data['energy_per_total_token']
                })

        if power_draw_data:
            generate_average_power_draw_chart(power_draw_data, output_dir, 'average_power_draw_chart.png')
        if model_power_data:
            generate_model_average_power_chart(model_power_data, output_dir, 'model_average_power_chart.png')
        if power_draw_data:
            generate_detailed_power_charts(power_draw_data, output_dir)
    except Exception as e:
        print(f"Error processing average power data: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate plots from evaluation results.")
    parser.add_argument('--config', required=True, help='Path to the configuration file.')
    parser.add_argument('--results_dir', required=True, help='Path to the evaluation results directory.')
    parser.add_argument('--output_dir', required=True, help='Path to the output directory for plots.')

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs('snakeout/plots', exist_ok=True)

    # Load configuration and run the processing function
    config = load_config(args.config)
    process_evaluation_results(config, args.results_dir, args.output_dir)

    # Process average power consumption data and generate visualizations
    process_average_power_data(args.results_dir, args.output_dir)
