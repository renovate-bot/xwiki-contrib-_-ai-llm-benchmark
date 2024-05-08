# LLM AI Evaluation framework

Evaluation framework for AI models in the context of the LLM project.

There are already a lot of evaluations that cover various aspects of LLMs.
The main goal of our evaluation is to evaluate the suitability of self-hosted LLMs for specific tasks in the context 
of knowledge management and XWiki technical support questions in particular.

Apart from performance on the tasks, we want to measure the energetic costs of the LLMs.

Further, for every LLM an ethics rating will be provided.
It evaluates the license of the model, license of training data, license of training and inference software, and 
possibly other criteria.

Evaluated tasks:

* generating typical content
* content summarization
* question answering (based on provided context)

All tasks will be evaluated in several languages, most likely German, French and English as these are most relevant for XWiki.

The context documents are, unless otherwise stated, documents from www.xwiki.org, licensed under a Creative Commons 
Attribution license.
The source URL is provided in every document.

* Project Lead: Ludovic Dubost 
* Documentation & Downloads: [Documentation & Download](https://extensions.xwiki.org/xwiki/bin/view/Extension/LLM%20Application/) 
* [Issue Tracker](https://jira.xwiki.org/browse/LLMAI)
* Communication: [Forum](https://forum.xwiki.org/), [Chat](https://dev.xwiki.org/xwiki/bin/view/Community/Chat)
* [Development Practices](https://dev.xwiki.org)
* Minimal XWiki version supported: XWiki 16.2.0
* License: LGPL 2.1
* Translations: N/A
* Sonar Dashboard: N/A
* Continuous Integration Status: N/A
