import os
import sys
import json
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.metrics import FaithfulnessMetric
from deepeval.metrics import ContextualRecallMetric
from deepeval.metrics import ContextualPrecisionMetric
from deepeval.metrics import ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase

# Add the parent directory of the 'scripts' folder to the Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evaluation_utils import load_config, save_evaluation_result, get_evaluator_model

def calculate_ragas_score(ai_qa_file, evaluator_model):
    # Load the AI-generated QA file
    with open(ai_qa_file, 'r') as file:
        qa_data = json.load(file)

    # Extract the input prompt, expected answer, and the generated answer
    prompt = qa_data['prompt']
    expected_answer = qa_data['expected_answer']
    ai_answer = qa_data['ai_answer']
    retrieval_context = [source['content'] for source in qa_data.get('sources', [])]

    # Create the test case
    test_case = LLMTestCase(
        input=prompt,
        expected_output=expected_answer,
        actual_output=ai_answer,
        retrieval_context=retrieval_context
    )

    ar_metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=evaluator_model,
        include_reason=True
    )

    faithfulness_metric = FaithfulnessMetric(
        threshold=0.7,
        model=evaluator_model,
        include_reason=True
    )

    cp_metric = ContextualPrecisionMetric(
        threshold=0.7,
        model=evaluator_model,
        include_reason=True
    )

    cr_metric = ContextualRecallMetric(
        threshold=0.7,
        model=evaluator_model,
        include_reason=True
    )

    # Measure the test case
    ar_metric.measure(test_case)
    faithfulness_metric.measure(test_case)
    cp_metric.measure(test_case)
    cr_metric.measure(test_case)

    average_score = (ar_metric.score
                     + faithfulness_metric.score 
                     + cp_metric.score 
                     + cr_metric.score) / 4
    
    individual_scores = {
        "AnswerRelevancy": ar_metric.score,
        "Faithfulness": faithfulness_metric.score,
        "ContextualPrecision": cp_metric.score,
        "ContextualRecall": cr_metric.score
    }
    reasons = {
        "AnswerRelevancy": ar_metric.reason,
        "Faithfulness": faithfulness_metric.reason,
        "ContextualPrecision": cp_metric.reason,
        "ContextualRecall": cr_metric.reason
    }

    return average_score, individual_scores, reasons

def evaluate_rag_qa_task(qa_file, evaluator_model, evaluation_dir):
    average_score, individual_scores, reasons = calculate_ragas_score(qa_file, evaluator_model)
    evaluation_result = {
        "average_score": average_score,
        "individual_scores": individual_scores,
        "reasons": reasons
    }

    result_file = os.path.join(evaluation_dir, f"{os.path.splitext(os.path.basename(qa_file))[0]}_result.json")
    save_evaluation_result(result_file, evaluation_result)

def evaluate_rag_qa(output_dir, evaluation_dir, config_file):
    config = load_config(config_file)
    evaluator_model = get_evaluator_model(config_file)

    for task in config['tasks']:
        if task['task'] == 'RAG-qa':
            model_name = task['settings']['model']
            model_output_dir = os.path.join(output_dir, model_name, 'tasks', 'RAG-qa')
            model_evaluation_dir = os.path.join(evaluation_dir, model_name)
            os.makedirs(model_evaluation_dir, exist_ok=True)

            if os.path.exists(model_output_dir):
                for qa_file in os.listdir(model_output_dir):
                    if qa_file.endswith('.json'):
                        qa_file_path = os.path.join(model_output_dir, qa_file)
                        result_file = os.path.join(model_evaluation_dir, f"{os.path.splitext(qa_file)[0]}_result.json")

                        # Check if the result file already exists
                        if not os.path.exists(result_file):
                            evaluate_rag_qa_task(qa_file_path, evaluator_model, model_evaluation_dir)
                        else:
                            print(f"Skipping evaluation for {model_name} - {qa_file} as it has already been evaluated.")

def main(output_dir, evaluation_dir, config_file):
    evaluate_rag_qa(output_dir, evaluation_dir, config_file)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate RAG-qa tasks using RAGAS metric.')
    parser.add_argument('--output-dir', required=True, help='Directory containing the output files')
    parser.add_argument('--evaluation-dir', required=True, help='Directory to store the evaluation results')
    parser.add_argument('--config-file', default='config.json', help='Path to the configuration file')
    os.makedirs("snakeout/evaluated_rag_qa", exist_ok=True)
    args = parser.parse_args()

    main(args.output_dir, args.evaluation_dir, args.config_file)
