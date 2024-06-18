import json
import os

# Define variables for repeating elements
CONFIG_FILE = "config.json"
CONTEXT_DATA_DIR = "context_data"
INPUT_DIR = "input"
INPUT_JSON_FILE = f"{INPUT_DIR}/input.json"
TASKS_DIR = f"{INPUT_DIR}/tasks"
SCRIPTS_DIR = "scripts"
OUTPUT_DIR = "output"
EVALUATION_DIR = "evaluation_results"


RESULTS_SUMMARIZATION_DIR = f"{EVALUATION_DIR}/summarization"
RESULTS_TEXT_GENERATION_DIR = f"{EVALUATION_DIR}/text_generation"
RESULTS_QA_DIR = f"{EVALUATION_DIR}/RAG-qa"

PLOTS_DIR = "evaluation_results_graphics"

SNAKEOUT_DIR = "snakeout"
SNAKEOUT_INDEXED = f"{SNAKEOUT_DIR}/indexed"
SNAKEOUT_COLLECTED = f"{SNAKEOUT_DIR}/collected"
SNAKEOUT_EVALUATED_SUMMARIES = f"{SNAKEOUT_DIR}/evaluated_summaries"
SNAKEOUT_EVALUATED_TEXTGEN = f"{SNAKEOUT_DIR}/evaluated_textgen"
SNAKEOUT_EVALUATED_RAG_QA = f"{SNAKEOUT_DIR}/evaluated_rag_qa"
SNAKEOUT_AVERAGE_POWER = f"{SNAKEOUT_DIR}/average_power"

rule all:
    input:
        TASKS_DIR,
        SNAKEOUT_COLLECTED,
        SNAKEOUT_EVALUATED_SUMMARIES,
        SNAKEOUT_EVALUATED_TEXTGEN,
        SNAKEOUT_EVALUATED_RAG_QA,
        SNAKEOUT_AVERAGE_POWER,
        PLOTS_DIR

rule index_data:
    input:
        script = f"{SCRIPTS_DIR}/context_indexing/index_data.py"
    output:
        directory(SNAKEOUT_INDEXED)
    params:
        collections_dir = f"{CONTEXT_DATA_DIR}/collections",
        documents_dir = f"{CONTEXT_DATA_DIR}/documents"
    shell:
        "python {input.script} --collections-dir {params.collections_dir} --documents-dir {params.documents_dir} --output-dir {output}"

rule split_input_to_files:
    input:
        script = f"{SCRIPTS_DIR}/input_data_preparation/split_input_to_files.py",
        dependency = SNAKEOUT_INDEXED,
        input_json = INPUT_JSON_FILE
    output:
        directory(TASKS_DIR)
    params:
        file = INPUT_JSON_FILE
    shell:
        "python {input.script} --input-file {params.file} --output-dir {output}"

rule collect_model_responses:
    input:
        dependency = TASKS_DIR,
        dependency2 = CONFIG_FILE,
        input_json = INPUT_JSON_FILE,
        script = f"{SCRIPTS_DIR}/output_generation/collect_model_responses.py"
    output:
        directory(SNAKEOUT_COLLECTED)
    params:
        input_dir = TASKS_DIR,
        output_dir = OUTPUT_DIR,
        file = CONFIG_FILE
    shell:
        "python {input.script} --input-dir {params.input_dir} --output-dir {params.output_dir} --request-template {params.file}"

rule eval_summary:
    input:
        dependency = TASKS_DIR,
        dependency2 = SNAKEOUT_COLLECTED,
        dependency3 = INPUT_JSON_FILE,
        config_file = CONFIG_FILE,
        script = f"{SCRIPTS_DIR}/evaluation_scripts/eval_summary.py"
    output:
        directory(SNAKEOUT_EVALUATED_SUMMARIES)
    params:
        evaluation_dir = RESULTS_SUMMARIZATION_DIR,
        output_dir = OUTPUT_DIR,
        threshold = 0.5
    shell:
        "python {input.script} --output-dir {params.output_dir} --evaluation-dir {params.evaluation_dir} --config-file {input.config_file} --threshold {params.threshold}"

rule eval_text_generation:
    input:
        dependency = TASKS_DIR,
        dependency2 = SNAKEOUT_COLLECTED,
        dependency3 = INPUT_JSON_FILE,
        config_file = CONFIG_FILE,
        script = f"{SCRIPTS_DIR}/evaluation_scripts/eval_text_generation.py"
    output:
        directory(SNAKEOUT_EVALUATED_TEXTGEN)
    params:
        evaluation_dir = RESULTS_TEXT_GENERATION_DIR,
        output_dir = OUTPUT_DIR
    shell:
        "python {input.script} --output-dir {params.output_dir} --evaluation-dir {params.evaluation_dir} --config-file {input.config_file}"

rule eval_rag_qa:
    input:
        dependency = TASKS_DIR,
        dependency2 = SNAKEOUT_COLLECTED,
        dependency3 = INPUT_JSON_FILE,
        config_file = CONFIG_FILE,
        script = f"{SCRIPTS_DIR}/evaluation_scripts/eval_rag_qa.py"
    output:
        directory(SNAKEOUT_EVALUATED_RAG_QA)
    params:
        evaluation_dir = RESULTS_QA_DIR,
        output_dir = OUTPUT_DIR
    shell:
        "python {input.script} --output-dir {params.output_dir} --evaluation-dir {params.evaluation_dir} --config-file {input.config_file}"

rule create_plots:
    input:
        config_file = CONFIG_FILE,
        results_dir = EVALUATION_DIR
    output:
        directory(PLOTS_DIR)
    params:
        script = f"{SCRIPTS_DIR}/results_visualization/create_plots.py"
    shell:
        "python {params.script} --config {input.config_file} --results_dir {input.results_dir} --output_dir {output}"

rule calculate_average_power:
    input:
        dependency = SNAKEOUT_COLLECTED,
        script = f"{SCRIPTS_DIR}/evaluation_scripts/calculate_average_power.py"
    output:
        directory(SNAKEOUT_AVERAGE_POWER)
    params:
        evaluation_dir = OUTPUT_DIR,
        output_dir = EVALUATION_DIR
    shell:
        "python {input.script} --evaluation-dir {params.evaluation_dir} --output-dir {params.output_dir}"

rule clean:
    shell:
        """
        rm -rf {EVALUATION_DIR}/ {TASKS_DIR}/ {OUTPUT_DIR}/* {SNAKEOUT_DIR}/ {PLOTS_DIR}/*
        """
