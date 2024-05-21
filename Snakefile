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
INDEXED_DIR = f"{SNAKEOUT_DIR}/indexed"

rule all:
    input:
        INDEXED_DIR,
        TASKS_DIR,
        OUTPUT_DIR,
        RESULTS_SUMMARIZATION_DIR,
        RESULTS_TEXT_GENERATION_DIR,
        RESULTS_QA_DIR,
        PLOTS_DIR

rule index_data:
    input:
        script = f"{SCRIPTS_DIR}/context_indexing/index_data.py"
    output:
        directory(INDEXED_DIR)
    params:
        collections_dir = f"{CONTEXT_DATA_DIR}/collections",
        documents_dir = f"{CONTEXT_DATA_DIR}/documents"
    shell:
        "python {input.script} --collections-dir {params.collections_dir} --documents-dir {params.documents_dir} --output-dir {output}"

rule split_input_to_files:
    input:
        script = f"{SCRIPTS_DIR}/input_data_preparation/split_input_to_files.py",
        dependency = INDEXED_DIR
    output:
        directory(TASKS_DIR)
    params:
        file = INPUT_JSON_FILE
    shell:
        "python {input.script} --input-file {params.file} --output-dir {output}"

rule collect_model_responses:
    input:
        dependency = TASKS_DIR,
        script = f"{SCRIPTS_DIR}/output_generation/collect_model_responses.py"
    output:
        directory(OUTPUT_DIR)
    params:
        input_dir = TASKS_DIR,
        file = CONFIG_FILE
    shell:
        "python {input.script} --input-dir {params.input_dir} --output-dir {output} --request-template {params.file}"

rule update_output:
    shell:
        "python scripts/output_generation/collect_model_responses.py --input-dir input/tasks --output-dir output --request-template config.json"

rule eval_summary:
    input:
        script = f"{SCRIPTS_DIR}/evaluation_scripts/eval_summary.py",
        output_dir = OUTPUT_DIR,
        config_file = CONFIG_FILE
    output:
        directory(RESULTS_SUMMARIZATION_DIR)
    params:
        evaluation_dir = RESULTS_SUMMARIZATION_DIR
    shell:
        "python {input.script} --output-dir {input.output_dir} --evaluation-dir {params.evaluation_dir} --config-file {input.config_file}"

rule eval_text_generation:
    input:
        script = f"{SCRIPTS_DIR}/evaluation_scripts/eval_text_generation.py",
        output_dir = OUTPUT_DIR,
        config_file = CONFIG_FILE
    output:
        directory(RESULTS_TEXT_GENERATION_DIR)
    params:
        evaluation_dir = RESULTS_TEXT_GENERATION_DIR
    shell:
        "python {input.script} --output-dir {input.output_dir} --evaluation-dir {params.evaluation_dir} --config-file {input.config_file}"

rule eval_rag_qa:
    input:
        script = f"{SCRIPTS_DIR}/evaluation_scripts/eval_rag_qa.py",
        output_dir = OUTPUT_DIR,
        config_file = CONFIG_FILE
    output:
        directory(RESULTS_QA_DIR)
    params:
        evaluation_dir = RESULTS_QA_DIR
    shell:
        "python {input.script} --output-dir {input.output_dir} --evaluation-dir {params.evaluation_dir} --config-file {input.config_file}"

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


rule clean:
    shell:
        """
        rm -rf {EVALUATION_DIR}/ {TASKS_DIR}/ {OUTPUT_DIR}/ {SNAKEOUT_DIR}/
        """
