import os
import sys
from langdetect import detect

# Add the parent directory of the 'scripts' folder to the Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evaluation_utils import load_config, save_evaluation_result, get_evaluator_model

import json
from deepeval import evaluate
from deepeval.metrics import SummarizationMetric
from deepeval.test_case import LLMTestCase

def measure_metric_with_retry(metric, test_case, max_retries=3):
    for attempt in range(max_retries + 1):
        try:
            metric.measure(test_case)
            return metric.score, metric.reason, metric.score_breakdown
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for SummarizationMetric: {str(e)}")
            if attempt == max_retries:
                return 0, f"Failed to measure after {max_retries + 1} attempts: {str(e)}", {}

def calculate_summary_score(ai_summary_file, evaluator_model, threshold=0.5):
    with open(ai_summary_file, 'r') as file:
        summary_data = json.load(file)

    input_text = summary_data['prompt']
    generated_summary = summary_data['ai_answer']

    # Add defensive checks for empty text
    try:
        input_language = detect(input_text) if input_text.strip() else 'unknown'
        summary_language = detect(generated_summary) if generated_summary.strip() else 'unknown'
    except Exception as e:
        print(f"Language detection failed: {str(e)}")
        input_language = 'unknown'
        summary_language = 'unknown'

    test_case = LLMTestCase(input=input_text, actual_output=generated_summary)
    metric = SummarizationMetric(threshold=threshold, model=evaluator_model)
    
    score, reason, score_breakdown = measure_metric_with_retry(metric, test_case)

    return score, reason, score_breakdown, input_language, summary_language

def evaluate_summary(summary_file, evaluator_model, evaluation_dir, threshold=0.5):
    score, reason, score_breakdown, input_language, summary_language = calculate_summary_score(summary_file, evaluator_model, threshold)
    evaluation_result = {
        "score": score,
        "reason": reason,
        "score_breakdown": score_breakdown,
        "input_language": input_language,
        "summary_language": summary_language
    }

    result_file = os.path.join(evaluation_dir, f"{os.path.splitext(os.path.basename(summary_file))[0]}_result.json")
    save_evaluation_result(result_file, evaluation_result)


def evaluate_summaries(output_dir, evaluation_dir, config_file, threshold=0.5):
    config = load_config(config_file)
    evaluator_model = get_evaluator_model(config_file)

    for task in config['tasks']:
        if task['task'] == 'summarization':
            model_name = task['settings']['model']
            model_output_dir = os.path.join(output_dir, model_name, 'tasks', 'summarization')
            model_evaluation_dir = os.path.join(evaluation_dir, model_name)
            os.makedirs(model_evaluation_dir, exist_ok=True)

            if os.path.exists(model_output_dir):
                for summary_file in os.listdir(model_output_dir):
                    if summary_file.endswith('.json'):
                        summary_file_path = os.path.join(model_output_dir, summary_file)
                        result_file = os.path.join(model_evaluation_dir, f"{os.path.splitext(summary_file)[0]}_result.json")

                        # Check if the result file already exists
                        if not os.path.exists(result_file):
                            evaluate_summary(summary_file_path, evaluator_model, model_evaluation_dir, threshold)
                        else:
                            print(f"Skipping evaluation for {model_name} - {summary_file} as it has already been evaluated.")

def main(output_dir, evaluation_dir, config_file, threshold=0.5):
    evaluate_summaries(output_dir, evaluation_dir, config_file, threshold)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate summaries using DeepEval.')
    parser.add_argument('--output-dir', required=True, help='Directory containing the output files')
    parser.add_argument('--evaluation-dir', required=True, help='Directory to store the evaluation results')
    parser.add_argument('--config-file', default='config.json', help='Path to the configuration file')
    parser.add_argument('--threshold', type=float, default=0.5, help='Threshold for the SummarizationMetric')
    os.makedirs("snakeout/evaluated_summaries", exist_ok=True)
    args = parser.parse_args()

    main(args.output_dir, args.evaluation_dir, args.config_file, args.threshold)
    
