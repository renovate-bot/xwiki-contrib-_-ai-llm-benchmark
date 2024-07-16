import os
import sys
import json
from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from langdetect import detect

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

    # Detect languages
    prompt_language = detect(prompt)
    expected_answer_language = detect(expected_answer)
    generated_text_language = detect(generated_text)

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

    return metric.score, metric.reason, prompt_language, expected_answer_language, generated_text_language

def evaluate_text_generation_task(generated_file, evaluator_model, evaluation_dir):
    score, reason, prompt_language, expected_answer_language, generated_text_language = calculate_text_generation_score(generated_file, evaluator_model)
    evaluation_result = {
        "score": score,
        "reason": reason,
        "prompt_language": prompt_language,
        "expected_answer_language": expected_answer_language,
        "generated_text_language": generated_text_language
    }

    result_file = os.path.join(evaluation_dir, f"{os.path.splitext(os.path.basename(generated_file))[0]}_result.json")
    save_evaluation_result(result_file, evaluation_result)

def evaluate_text_generation(output_dir, evaluation_dir, config_file):
    config = load_config(config_file)
    evaluator_model = get_evaluator_model(config_file)

    for task in config['tasks']:
        if task['task'] == 'text_generation':
            model_name = task['settings']['model']
            model_output_dir = os.path.join(output_dir, model_name, 'tasks', 'text_generation')
            model_evaluation_dir = os.path.join(evaluation_dir, model_name)
            os.makedirs(model_evaluation_dir, exist_ok=True)

            if os.path.exists(model_output_dir):
                for generated_file in os.listdir(model_output_dir):
                    if generated_file.endswith('.json'):
                        generated_file_path = os.path.join(model_output_dir, generated_file)
                        result_file = os.path.join(model_evaluation_dir, f"{os.path.splitext(generated_file)[0]}_result.json")

                        # Check if the result file already exists
                        if not os.path.exists(result_file):
                            evaluate_text_generation_task(generated_file_path, evaluator_model, model_evaluation_dir)
                        else:
                            print(f"Skipping evaluation for {model_name} - {generated_file} as it has already been evaluated.")

def main(output_dir, evaluation_dir, config_file):
    evaluate_text_generation(output_dir, evaluation_dir, config_file)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate text generation using DeepEval.')
    parser.add_argument('--output-dir', required=True, help='Directory containing the output files')
    parser.add_argument('--evaluation-dir', required=True, help='Directory to store the evaluation results')
    parser.add_argument('--config-file', default='config.json', help='Path to the configuration file')
    os.makedirs("snakeout/evaluated_textgen", exist_ok=True)
    args = parser.parse_args()

    main(args.output_dir, args.evaluation_dir, args.config_file)
