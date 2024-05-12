rule all:
    input:
        "input/prompts",
        "snakeout/indexed",
        "output",
        "evaluation/results",
        "evaluation/plots"

rule split_input_to_files:
    input:
        "input/input.json"
    output:
        directory("input/prompts")
    params:
        script = "scripts/split_input_to_files.py"
    shell:
        "python {params.script} --input-file {input} --output-dir {output}"

rule index_data:
    input:
        collections_dir = "context_data/collections",
        documents_dir = "context_data/documents"
    output:
        directory("snakeout/indexed")
    params:
        script = "scripts/index_data.py"
    shell:
        "python {params.script} --collections-dir {input.collections_dir} --documents-dir {input.documents_dir} --output-dir {output}"

rule collect_data:
    input:
        input_dir = "input/prompts",
        request_template = "request.json"
    output:
        directory("output")
    params:
        script = "scripts/collect_data.py"
    shell:
        "python {params.script} --input-dir {input.input_dir} --output-dir {output} --request-template {input.request_template}"

rule calculate_scores:
    input:
        output_dir = "output"
    output:
        directory("evaluation/results")
    params:
        script = "scripts/calculate_scores.py"
    shell:
        "python {params.script} --output-dir {input.output_dir} --results-dir {output}"

rule create_plots:
    input:
        results_dir = "evaluation/results"
    output:
        directory("evaluation/plots")
    params:
        script = "scripts/create_plots.py"
    shell:
        "python {params.script} --results-dir {input.results_dir} --plots-dir {output}"
