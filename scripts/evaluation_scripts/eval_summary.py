import os
import sys
import json
from deepeval import evaluate
from deepeval.metrics import SummarizationMetric
from deepeval.test_case import LLMTestCase

# Add the parent directory of the 'scripts' folder to the Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evaluation_utils import load_config, save_evaluation_result, get_evaluator_model

def calculate_summary_score(ai_summary_file, evaluator_model):
    # Load the AI-generated summary file
    with open(ai_summary_file, 'r') as file:
        summary_data = json.load(file)

    # Extract the input text and the generated summary
    input_text = summary_data['prompt']
    generated_summary = summary_data['ai_answer']

    # Create the test case
    test_case = LLMTestCase(input=input_text, actual_output=generated_summary)

    # Create the evaluation metric
    metric = SummarizationMetric(
        threshold=0.5,
        model=evaluator_model
    )

    # Measure the test case
    metric.measure(test_case)

    return metric.score, metric.reason, metric.score_breakdown

def evaluate_summaries(output_dir, evaluation_dir, config_file):
    config = load_config(config_file)
    evaluator_model = get_evaluator_model(config_file)

    for task in config['tasks']:
        if task['task'] == 'summarization':
            model_name = task['settings']['model']
            model_output_dir = os.path.join(output_dir, model_name)
            if os.path.isdir(model_output_dir):
                model_evaluation_dir = os.path.join(evaluation_dir, model_name)
                os.makedirs(model_evaluation_dir, exist_ok=True)

                summarization_dir = os.path.join(model_output_dir, 'tasks', 'summarization')
                if os.path.exists(summarization_dir):
                    for summary_file in os.listdir(summarization_dir):
                        if summary_file.endswith('.json'):
                            ai_summary_file = os.path.join(summarization_dir, summary_file)
                            result_file = os.path.join(model_evaluation_dir, f"{os.path.splitext(summary_file)[0]}_result.json")

                            score, reason, score_breakdown = calculate_summary_score(ai_summary_file, evaluator_model)
                            evaluation_result = {
                                "score": score,
                                "reason": reason,
                                "score_breakdown": score_breakdown
                            }
                            save_evaluation_result(result_file, evaluation_result)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate summaries using DeepEval.')
    parser.add_argument('--output-dir', required=True, help='Directory containing the output files')
    parser.add_argument('--evaluation-dir', required=True, help='Directory to store the evaluation results')
    parser.add_argument('--config-file', default='config.json', help='Path to the configuration file')

    args = parser.parse_args()

    evaluate_summaries(args.output_dir, args.evaluation_dir, args.config_file)