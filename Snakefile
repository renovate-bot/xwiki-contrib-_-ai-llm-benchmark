# Define variables for repeating elements
SCRIPTS_DIR = "scripts"
CONTEXT_DATA_DIR = "context_data"
INPUT_DIR = "input"
OUTPUT_DIR = "output"
SNAKEOUT_DIR = "snakeout"
EVALUATION_DIR = "evaluation"
TASKS_DIR = f"{INPUT_DIR}/tasks"
INDEXED_DIR = f"{SNAKEOUT_DIR}/indexed"
QA_OUTPUT_DIR = f"{OUTPUT_DIR}/tasks/qa"
SUMMARIZATION_INPUT_FILE = f"{INPUT_DIR}/summarization.json"
RESULTS_SUMMARIZATION_DIR = f"{EVALUATION_DIR}/results_summarization"
RESULTS_QA_DIR = f"{EVALUATION_DIR}/results_qa"
PLOTS_DIR = f"{EVALUATION_DIR}/plots"
CONFIG_FILE = "config.json"
INPUT_JSON_FILE = f"{INPUT_DIR}/input.json"

rule all:
    input:
        INDEXED_DIR,
        TASKS_DIR,
        QA_OUTPUT_DIR

rule index_data:
    input:
        script = f"{SCRIPTS_DIR}/index_data.py"
    output:
        directory(INDEXED_DIR)
    params:
        collections_dir = f"{CONTEXT_DATA_DIR}/collections",
        documents_dir = f"{CONTEXT_DATA_DIR}/documents"
    shell:
        "python {input.script} --collections-dir {params.collections_dir} --documents-dir {params.documents_dir} --output-dir {output}"

rule split_input_to_files:
    input:
        script = f"{SCRIPTS_DIR}/split_input_to_files.py",
        dependency = INDEXED_DIR
    output:
        directory(TASKS_DIR)
    params:
        file = INPUT_JSON_FILE
    shell:
        "python {input.script} --input-file {params.file} --output-dir {output}"

rule collect_model_response:
    input:
        dependency = TASKS_DIR,
        script = f"{SCRIPTS_DIR}/collect_model_responses.py"
    output:
        directory(QA_OUTPUT_DIR)
    params:
        input_dir = f"{TASKS_DIR}/qa",
        file = CONFIG_FILE
    shell:
        "python {input.script} --input-dir {params.input_dir} --output-dir {output} --request-template {params.file}"

# Uncomment and update the following rules as needed

rule test_eval_summary:
    input:
        SUMMARIZATION_INPUT_FILE
    output:
        directory(RESULTS_SUMMARIZATION_DIR)
    params:
        script = f"{SCRIPTS_DIR}/test_eval_summary.py"
    shell:
        "python {params.script} --input-file {input} --results-dir {output}"

# rule calculate_scores:
#     input:
#         output_dir = QA_OUTPUT_DIR
#     output:
#         directory(RESULTS_QA_DIR)
#     params:
#         script = f"{SCRIPTS_DIR}/calculate_scores.py"
#     shell:
#         "python {params.script} --output-dir {input.output_dir} --results-dir {output}"

# rule create_plots:
#     input:
#         results_dir = RESULTS_QA_DIR
#     output:
#         directory(PLOTS_DIR)
#     params:
#         script = f"{SCRIPTS_DIR}/create_plots.py"
#     shell:
#         "python {params.script} --results-dir {input.results_dir} --plots-dir {output}"

rule clean:
    shell:
        """
        rm -rf {EVALUATION_DIR}/ {TASKS_DIR}/ {OUTPUT_DIR}/ {SNAKEOUT_DIR}/
        """
