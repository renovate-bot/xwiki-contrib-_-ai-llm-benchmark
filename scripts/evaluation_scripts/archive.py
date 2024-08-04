import os
import shutil
import datetime
import argparse

def create_archive(input_dir, output_dir, evaluation_dir, reports_dir, config_file, archive_dir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"ai_llm_benchmark_archive_{timestamp}"
    archive_path = os.path.join(archive_dir, archive_name)

    os.makedirs(archive_path, exist_ok=True)

    # Copy input, output, and evaluation_results directories
    shutil.copytree(input_dir, os.path.join(archive_path, "input"))
    shutil.copytree(output_dir, os.path.join(archive_path, "output"))
    shutil.copytree(evaluation_dir, os.path.join(archive_path, "evaluation_results"))

    # Copy PDF reports
    os.makedirs(os.path.join(archive_path, "reports"), exist_ok=True)
    for report in os.listdir(reports_dir):
        if report.endswith('.pdf'):
            shutil.copy2(os.path.join(reports_dir, report), os.path.join(archive_path, "reports"))

    # Copy config.json
    shutil.copy2(config_file, os.path.join(archive_path, "config.json"))

    # Create a zip file of the archive
    shutil.make_archive(archive_path, 'zip', archive_path)

    # Remove the temporary directory
    shutil.rmtree(archive_path)

    print(f"Archive created: {archive_path}.zip")
    print(f"Previous archives in {archive_dir} have been preserved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an archive of the AI LLM benchmark results")
    parser.add_argument("--input-dir", required=True, help="Path to the input directory")
    parser.add_argument("--output-dir", required=True, help="Path to the output directory")
    parser.add_argument("--evaluation-dir", required=True, help="Path to the evaluation results directory")
    parser.add_argument("--reports-dir", required=True, help="Path to the reports directory")
    parser.add_argument("--config-file", required=True, help="Path to the config.json file")
    parser.add_argument("--archive-dir", required=True, help="Path to store the archive")

    args = parser.parse_args()

    create_archive(args.input_dir, args.output_dir, args.evaluation_dir, args.reports_dir, args.config_file, args.archive_dir)
