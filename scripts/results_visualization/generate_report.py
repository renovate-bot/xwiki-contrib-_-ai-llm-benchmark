import os
import re
import argparse
import json
import html
from datetime import datetime
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

criteria = {
    'summarization': ['Alignment', 'Coverage'],
    'text_generation': ['score'],
    'RAG-qa': ['AnswerRelevancy', 'Faithfulness', 'ContextualPrecision', 'ContextualRecall']
}

def create_pdf_document(output_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_file = os.path.join(output_dir, f"evaluation_report_{timestamp}.pdf")
    return SimpleDocTemplate(pdf_file, pagesize=letter)

def add_title(elements, styles):
    elements.append(Paragraph("LLM Evaluation Report", styles['Title']))
    elements.append(Spacer(1, 12))

def add_executive_summary(elements, styles, config, evaluation_results_dir):
    elements.append(Paragraph("Executive Summary", styles['Heading1']))
    # Add overall performance highlights and key findings
    # This would require analyzing the evaluation results
    elements.append(Spacer(1, 12))

def add_methodology(elements, styles, config):
    elements.append(Paragraph("Evaluation Criteria:", styles['Heading2']))
    for task, task_criteria in criteria.items():
        elements.append(Paragraph(f"{task.capitalize()}: {', '.join(task_criteria)}", styles['Normal']))
    elements.append(Spacer(1, 12))

def add_model_information(elements, styles, config):
    elements.append(Paragraph("Setup Information", styles['Heading1']))
    
    data = [["Task", "Model", "Temperature", "Power Measurement"]]
    
    for task in config['tasks']:
        task_name = task['task']
        model = task['settings']['model']
        temperature = task['settings']['temperature']
        power_measurement = "Yes" if task.get('power_measurement', False) else "No"
        data.append([task_name, model, temperature, power_measurement])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 12))


def add_task_results(elements, styles, config, plots_dir, evaluation_results_dir):
    unique_tasks = set(task['task'] for task in config['tasks'])
    
    for task_name in unique_tasks:
        elements.append(Paragraph(f"{task_name.capitalize()} Task Results", styles['Heading2']))
        elements.append(Spacer(1, 6))

        for criterion in criteria[task_name]:
            img_path = os.path.join(plots_dir, f'{task_name}_{criterion}_bar_chart.png')
            if os.path.exists(img_path):
                img = Image(img_path, width=400, height=300)
                elements.append(img)
                elements.append(Spacer(1, 12))

        elements.append(Paragraph("Grouped Results", styles['Heading3']))
        grouped_img_path = os.path.join(plots_dir, f'{task_name}_grouped_bar_chart.png')
        if os.path.exists(grouped_img_path):
            img = Image(grouped_img_path, width=400, height=300)
            elements.append(img)
            elements.append(Spacer(1, 12))

def add_power_consumption_results(elements, styles, plots_dir):
    elements.append(Paragraph("Power Consumption Results", styles['Heading2']))
    elements.append(Spacer(1, 6))

    power_img_paths = [
        'average_power_draw_chart.png',
        'model_average_power_chart.png',
        'average_energy_consumption_grouped_chart.png',
        'average_energy_per_input_token_grouped_chart.png',
        'average_energy_per_output_token_grouped_chart.png',
        'average_energy_per_total_token_grouped_chart.png'
    ]

    for img_path in power_img_paths:
        full_img_path = os.path.join(plots_dir, img_path)
        if os.path.exists(full_img_path):
            img = Image(full_img_path, width=400, height=300)
            elements.append(img)
            elements.append(Spacer(1, 12))

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def add_evaluation_results(elements, styles, evaluation_results_dir):
    elements.append(Paragraph("Evaluation Results", styles['Heading1']))
    
    italic_style = ParagraphStyle(
        'Italic',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique'
    )
    
    if not os.path.exists(evaluation_results_dir):
        elements.append(Paragraph("No evaluation results found.", styles['Normal']))
        return
    
    for task_name in sorted(os.listdir(evaluation_results_dir)):
        task_dir = os.path.join(evaluation_results_dir, task_name)
        if os.path.isdir(task_dir):
            elements.append(Paragraph(f"{task_name.capitalize()} Results", styles['Heading2']))
            for model_dir in sorted(os.listdir(task_dir)):
                model_path = os.path.join(task_dir, model_dir)
                if os.path.isdir(model_path):
                    elements.append(Paragraph(f"Model: {model_dir}", styles['Heading3']))
                    result_files = [f for f in os.listdir(model_path) if f.endswith('.json')]
                    for result_file in sorted(result_files, key=natural_sort_key):
                        try:
                            with open(os.path.join(model_path, result_file), 'r') as f:
                                result_data = json.load(f)
                            elements.append(Paragraph(f"File: {result_file}", styles['Heading4']))
                            
                            for key, value in result_data.items():
                                if isinstance(value, dict):
                                    elements.append(Paragraph(f"<i>{key.capitalize()}:</i>", italic_style))
                                    for sub_key, sub_value in value.items():
                                        elements.append(Paragraph(f"  <i>{sub_key}:</i> {sub_value}", styles['Normal']))
                                else:
                                    elements.append(Paragraph(f"<i>{key.capitalize()}:</i> {value}", styles['Normal']))
                            
                            elements.append(Spacer(1, 12))
                        except json.JSONDecodeError:
                            elements.append(Paragraph(f"Error reading file: {result_file}", styles['Normal']))

def add_model_outputs(elements, styles, model_outputs_dir):
    elements.append(Paragraph("Model Outputs", styles['Heading1']))
    for model_name in os.listdir(model_outputs_dir):
        model_dir = os.path.join(model_outputs_dir, model_name)
        if os.path.isdir(model_dir):
            elements.append(Paragraph(f"Model: {model_name}", styles['Heading2']))
            tasks_dir = os.path.join(model_dir, 'tasks')
            if os.path.isdir(tasks_dir):
                for task_name in os.listdir(tasks_dir):
                    task_dir = os.path.join(tasks_dir, task_name)
                    if os.path.isdir(task_dir):
                        elements.append(Paragraph(f"{task_name.capitalize()} Outputs", styles['Heading3']))
                        for output_file in os.listdir(task_dir):
                            if output_file.endswith('.json'):
                                with open(os.path.join(task_dir, output_file), 'r') as f:
                                    output_data = json.load(f)
                                elements.append(Paragraph(f"File: {output_file}", styles['Heading4']))
                                elements.append(Paragraph("Prompt:", styles['Heading5']))
                                elements.append(Paragraph(html.escape(output_data.get('prompt', 'N/A')), styles['Normal']))
                                elements.append(Spacer(1, 6))
                                elements.append(Paragraph("AI Answer:", styles['Heading5']))
                                elements.append(Paragraph(html.escape(output_data.get('ai_answer', 'N/A')), styles['Normal']))
                                elements.append(Spacer(1, 12))

def generate_pdf_report(config, plots_dir, output_dir, evaluation_results_dir, model_outputs_dir):
    os.makedirs(output_dir, exist_ok=True)
    doc = create_pdf_document(output_dir)
    styles = getSampleStyleSheet()
    elements = []

    add_title(elements, styles)
    add_executive_summary(elements, styles, config, evaluation_results_dir)
    add_methodology(elements, styles, config)
    add_model_information(elements, styles, config)
    add_task_results(elements, styles, config, plots_dir, evaluation_results_dir)
    add_power_consumption_results(elements, styles, plots_dir)
    add_evaluation_results(elements, styles, evaluation_results_dir)
    add_model_outputs(elements, styles, model_outputs_dir)

    doc.build(elements)
    print(f"PDF report generated: {doc.filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PDF report from evaluation results.")
    parser.add_argument('--config', required=True, help='Path to the configuration file.')
    parser.add_argument('--plots_dir', required=True, help='Path to the directory containing plot images.')
    parser.add_argument('--output_dir', required=True, help='Path to the output directory for the PDF report.')
    parser.add_argument('--evaluation_results_dir', required=True, help='Path to the evaluation results directory.')
    parser.add_argument('--model_outputs_dir', required=True, help='Path to the model outputs directory.')

    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    generate_pdf_report(config, args.plots_dir, args.output_dir, args.evaluation_results_dir, args.model_outputs_dir)
