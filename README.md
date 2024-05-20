# LLM AI Evaluation framework

The LLM AI Evaluation Framework is a comprehensive tool designed to evaluate the performance and suitability of different Large Language Models (LLMs) for specific tasks in the context of knowledge management and XWiki technical support. The framework aims to provide insights into the capabilities of LLMs in generating typical content, summarizing content, and answering questions based on provided context.

The evaluation framework is built using Snakemake, a workflow management system that allows for the execution of the entire pipeline or individual steps. It integrates with the LLM Application's API to index and retrieve data, and utilizes various evaluation scripts to assess the performance of the LLMs on different tasks.

Evaluated tasks:

* generating typical content
* content summarization
* question answering (based on provided context)

All tasks will be evaluated in several languages, most likely German, French and English as these are most relevant for XWiki.

The context documents are, unless otherwise stated, documents from www.xwiki.org, licensed under a Creative Commons 
Attribution license.
The source URL is provided in every document.

## Usage

To use the LLM AI Evaluation framework, follow these steps:

1. Clone the repository:

```
git clone https://github.com/yourusername/llm-ai-evaluation.git
```

2. Navigate to the project directory:

```
cd llm-ai-evaluation
```

3. Create and activate the Conda environment:

```
conda env create -f environment.yml
conda activate snakemake
```

or update the environment:

```
conda env update --name snakemake --file environment.yml --prune
```

4. Customize the input/input.json and request.json according to your needs.

5. Run the pipeline with snakemake

```
snakemake --cores 1
```

* Project Lead: Ludovic Dubost 
* Documentation & Downloads: [Documentation & Download](https://extensions.xwiki.org/xwiki/bin/view/Extension/LLM%20Application/Evaluation%20framework/) 
* [Issue Tracker](https://jira.xwiki.org/browse/LLMAI)
* Communication: [Forum](https://forum.xwiki.org/), [Chat](https://dev.xwiki.org/xwiki/bin/view/Community/Chat)
* [Development Practices](https://dev.xwiki.org)
* Minimal XWiki version supported: XWiki 16.2.0
* License: LGPL 2.1
* Translations: N/A
* Sonar Dashboard: N/A
* Continuous Integration Status: N/A