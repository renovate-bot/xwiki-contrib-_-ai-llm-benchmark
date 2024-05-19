import os
import json
from scripts.models_connections.waise_model import WaiseModel
from scripts.models_connections.deepeval_model import EvaluatorModel

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def save_evaluation_result(result_file, evaluation_result):
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'w') as file:
        json.dump(evaluation_result, file, indent=2)

def get_evaluator_model(config_file):
    config = load_config(config_file)
    evaluator_settings = config['evaluator']

    return EvaluatorModel(WaiseModel(
        model=evaluator_settings['model'],
        temperature=evaluator_settings['temperature'],
        stream=evaluator_settings['stream'],
        verbose=False
    ))
