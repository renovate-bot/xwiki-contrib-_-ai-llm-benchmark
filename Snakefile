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
ARCHIVE_DIR = "archives"

RESULTS_SUMMARIZATION_DIR = f"{EVALUATION_DIR}/summarization"
RESULTS_TEXT_GENERATION_DIR = f"{EVALUATION_DIR}/text_generation"
RESULTS_QA_DIR = f"{EVALUATION_DIR}/RAG-qa"

PLOTS_DIR = "evaluation_results_graphics"
REPORTS_DIR = "reports"

SNAKEOUT_DIR = "snakeout"
SNAKEOUT_INDEXED = f"{SNAKEOUT_DIR}/indexed"
SNAKEOUT_COLLECTED = f"{SNAKEOUT_DIR}/collected"
SNAKEOUT_EVALUATED_SUMMARIES = f"{SNAKEOUT_DIR}/evaluated_summaries"
SNAKEOUT_EVALUATED_TEXTGEN = f"{SNAKEOUT_DIR}/evaluated_textgen"
SNAKEOUT_EVALUATED_RAG_QA = f"{SNAKEOUT_DIR}/evaluated_rag_qa"
SNAKEOUT_AVERAGE_POWER = f"{SNAKEOUT_DIR}/average_power"
SNAKEOUT_PLOTS = f"{SNAKEOUT_DIR}/plots"
SNAKEOUT_REPORTS = f"{SNAKEOUT_DIR}/reports"
SNAKEOUT_DIR_ARCHIVE = f"{SNAKEOUT_DIR}/archive"

rule evaluate:
    input:
        SNAKEOUT_EVALUATED_TEXTGEN,
        SNAKEOUT_EVALUATED_SUMMARIES,
        SNAKEOUT_EVALUATED_RAG_QA,
        SNAKEOUT_REPORTS

rule download:
    input:
        script = f"{SCRIPTS_DIR}/context_gathering/download_wiki_page.py",
        urls = "input/urls.txt"
    shell:
        "python {input.script} {input.urls}"

rule translate_to_french:
    input:
        script = f"{SCRIPTS_DIR}/translation/translate.py"
    output:
        directory(f"{CONTEXT_DATA_DIR}/documents_fr")
    params:
        language = "fr",
        collection = "Eval_FR"
    shell:
        "python {input.script} {params.language} {params.collection}"

rule translate_to_german:
    input:
        script = f"{SCRIPTS_DIR}/translation/translate.py"
    output:
        directory(f"{CONTEXT_DATA_DIR}/documents_de")
    params:
        language = "de",
        collection = "Eval_DE"
    shell:
        "python {input.script} {params.language} {params.collection}"

rule index:
    input:
        script = f"{SCRIPTS_DIR}/context_indexing/index_data.py"
    params:
        collections_dir = f"{CONTEXT_DATA_DIR}/collections",
        documents_dir = f"{CONTEXT_DATA_DIR}/documents"
    shell:
        "python {input.script} --collections-dir {params.collections_dir} --documents-dir {params.documents_dir}"

rule split:
    input:
        script = f"{SCRIPTS_DIR}/input_data_preparation/split_input_to_files.py",
        input_json = INPUT_JSON_FILE
    output:
        directory(TASKS_DIR)
    params:
        file = INPUT_JSON_FILE
    shell:
        "python {input.script} --input-file {params.file} --output-dir {output}"

rule collect:
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
        """
        python {input.script} --input-dir {params.input_dir} --output-dir {params.output_dir} --request-template {params.file}
        """

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
        """
        python {input.script} --output-dir {params.output_dir} --evaluation-dir {params.evaluation_dir} --config-file {input.config_file}
        """

rule generate_plots:
    input:
        config_file = CONFIG_FILE,
        results_dir = EVALUATION_DIR,
        dependency = SNAKEOUT_EVALUATED_RAG_QA,
        dependency2 = SNAKEOUT_AVERAGE_POWER,
    output:
        directory(SNAKEOUT_PLOTS)
    params:
        plots_dir = PLOTS_DIR,
        script = f"{SCRIPTS_DIR}/results_visualization/generate_plots.py"
    shell:
        """
        python {params.script} --config {input.config_file} --results_dir {input.results_dir} --output_dir {params.plots_dir}
        """

rule report:
    input:
        config_file = CONFIG_FILE,
        plots_dir = PLOTS_DIR,
        evaluation_results_dir = EVALUATION_DIR,
        model_outputs_dir = OUTPUT_DIR,
        dependency = SNAKEOUT_PLOTS,
        script = f"{SCRIPTS_DIR}/results_visualization/generate_report.py",
        models_info = "models_info.csv"
    output:
        directory(SNAKEOUT_REPORTS)
    params:
        report_dir=REPORTS_DIR
    shell:
        """
        python {input.script} --config {input.config_file} --plots_dir {input.plots_dir} --output_dir {params.report_dir} --evaluation_results_dir {input.evaluation_results_dir} --model_outputs_dir {input.model_outputs_dir} --models_info {input.models_info}
        """


rule generate_model_outputs_report:
    input:
        config_file = CONFIG_FILE,
        model_outputs_dir = OUTPUT_DIR,
        script = f"{SCRIPTS_DIR}/results_visualization/generate_report.py"
    output:
        directory(f"{SNAKEOUT_DIR}/model_outputs_report")
    params:
        report_dir = REPORTS_DIR
    shell:
        """
        python {input.script} --config {input.config_file} --model_outputs_dir {input.model_outputs_dir} --output_dir {params.report_dir} --plots_dir {PLOTS_DIR} --evaluation_results_dir {EVALUATION_DIR} --generate_model_outputs_only
        """


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

rule archive:
    input:
        script = f"{SCRIPTS_DIR}/evaluation_scripts/archive.py",
        input_dir = INPUT_DIR,
        output_dir = OUTPUT_DIR,
        evaluation_dir = EVALUATION_DIR,
        reports_dir = REPORTS_DIR,
        config_file = CONFIG_FILE,
        arhive_dir = ARCHIVE_DIR
    output:
        directory(SNAKEOUT_DIR_ARCHIVE)
    shell:
        """
        mkdir -p {output}
        python {input.script} --input-dir {input.input_dir} --output-dir {input.output_dir} --evaluation-dir {input.evaluation_dir} --reports-dir {input.reports_dir} --config-file {input.config_file} --archive-dir {input.arhive_dir}
        """


rule clean:
    shell:
        """
        rm -rf {EVALUATION_DIR}/ {TASKS_DIR}/ {OUTPUT_DIR}/* {SNAKEOUT_DIR} {PLOTS_DIR}/* {REPORTS_DIR}/.snakemake_timestamp
        mkdir -p {OUTPUT_DIR}
        mkdir -p {PLOTS_DIR}
        mkdir -p {RESULTS_SUMMARIZATION_DIR}
        mkdir -p {RESULTS_TEXT_GENERATION_DIR}
        mkdir -p {RESULTS_QA_DIR}
        """
