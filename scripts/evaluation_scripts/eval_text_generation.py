import os
import sys
import json
from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# Add the parent directory of the 'scripts' folder to the Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evaluation_utils import load_config, save_evaluation_result, get_evaluator_model

def calculate_text_generation_score(ai_generated_file, evaluator_model):
    # Load the AI-generated text file
    with open(ai_generated_file, 'r') as file:
        generated_data = json.load(file)

    # Extract the prompt and the generated text
    prompt = generated_data['prompt']
    generated_text = generated_data['ai_answer']
    expected_answer = generated_data['expected_answer']

    # Create the test case
    test_case = LLMTestCase(input=prompt, actual_output=generated_text, expected_output=expected_answer)

    # Create the evaluation metric
    metric = GEval(
        name="TextGenerationEvaluation",
        criteria="Evaluate the quality of the generated text based on its relevance to the prompt, coherence, and fluency.",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model=evaluator_model,
        strict_mode=False
    )

    # Measure the test case
    metric.measure(test_case)

    return metric.score, metric.reason, metric.score_breakdown

def evaluate_text_generation(output_dir, evaluation_dir, config_file):
    config = load_config(config_file)
    evaluator_model = get_evaluator_model(config_file)

    for task in config['tasks']:
        if task['task'] == 'text_generation':
            model_name = task['settings']['model']
            model_output_dir = os.path.join(output_dir, model_name)
            if os.path.isdir(model_output_dir):
                model_evaluation_dir = os.path.join(evaluation_dir, model_name)
                os.makedirs(model_evaluation_dir, exist_ok=True)

                text_generation_dir = os.path.join(model_output_dir, 'tasks', 'text_generation')
                if os.path.exists(text_generation_dir):
                    for generated_file in os.listdir(text_generation_dir):
                        if generated_file.endswith('.json'):
                            ai_generated_file = os.path.join(text_generation_dir, generated_file)
                            result_file = os.path.join(model_evaluation_dir, f"{os.path.splitext(generated_file)[0]}_result.json")

                            score, reason, score_breakdown = calculate_text_generation_score(ai_generated_file, evaluator_model)
                            evaluation_result = {
                                "score": score,
                                "reason": reason,
                                "score_breakdown": score_breakdown
                            }
                            save_evaluation_result(result_file, evaluation_result)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate text generation using DeepEval.')
    parser.add_argument('--output-dir', required=True, help='Directory containing the output files')
    parser.add_argument('--evaluation-dir', required=True, help='Directory to store the evaluation results')
    parser.add_argument('--config-file', default='config.json', help='Path to the configuration file')

    args = parser.parse_args()

    evaluate_text_generation(args.output_dir, args.evaluation_dir, args.config_file)