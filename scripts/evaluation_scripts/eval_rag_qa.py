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

from scripts.models_connections.waise_model import WaiseModel
from scripts.models_connections.deepeval_model import EvaluatorModel

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def save_evaluation_result(result_file, average_score, individual_scores, reasons):
    evaluation_result = {
        "average_score": average_score,
        "individual_scores": individual_scores,
        "reasons": reasons
    }
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'w') as file:
        json.dump(evaluation_result, file, indent=2)

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

def evaluate_rag_qa(output_dir, evaluation_dir, config_file):
    config = load_config(config_file)
    evaluator_settings = config['evaluator']

    evaluator_model = EvaluatorModel(WaiseModel(
        model=evaluator_settings['model'],
        temperature=evaluator_settings['temperature'],
        stream=evaluator_settings['stream'],
        verbose=False
    ))

    for model_dir in os.listdir(output_dir):
        model_output_dir = os.path.join(output_dir, model_dir)
        if os.path.isdir(model_output_dir):
            model_evaluation_dir = os.path.join(evaluation_dir, model_dir)
            os.makedirs(model_evaluation_dir, exist_ok=True)

            qa_dir = os.path.join(model_output_dir, 'tasks', 'RAG-qa')
            if os.path.exists(qa_dir):
                for qa_file in os.listdir(qa_dir):
                    if qa_file.endswith('.json'):
                        ai_qa_file = os.path.join(qa_dir, qa_file)
                        result_file = os.path.join(model_evaluation_dir, f"{os.path.splitext(qa_file)[0]}_result.json")

                        average_score, individual_scores, reasons = calculate_ragas_score(ai_qa_file, evaluator_model)
                        save_evaluation_result(result_file, average_score, individual_scores, reasons)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate RAG-qa tasks using RAGAS metric.')
    parser.add_argument('--output-dir', required=True, help='Directory containing the output files')
    parser.add_argument('--evaluation-dir', required=True, help='Directory to store the evaluation results')
    parser.add_argument('--config-file', default='config.json', help='Path to the configuration file')

    args = parser.parse_args()

    evaluate_rag_qa(args.output_dir, args.evaluation_dir, args.config_file)
