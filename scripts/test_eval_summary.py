from waise_model import WaiseModel
from deepeval_model import CustomModel
import json
from deepeval import evaluate
from deepeval.metrics import SummarizationMetric
from deepeval.test_case import LLMTestCase

waise_model = WaiseModel(model="AI.Models.llama3", temperature=0.2, stream=False, verbose=False)
deepeval_model = CustomModel(WaiseModel(model="AI.Models.llama3", temperature=0.2, stream=False, verbose=False))

with open('context_data/documents/xwiki_Documentation.UserGuide.Features.ContentOrganization.WebHome.json') as f:
    context = json.load(f)

input = context['content']

## The text to be summarized
# input = """
# The 'coverage score' is calculated as the percentage of assessment questions
# for which both the summary and the original document provide a 'yes' answer. This
# method ensures that the summary not only includes key information from the original
# text but also accurately represents it. A higher coverage score indicates a
# more comprehensive and faithful summary, signifying that the summary effectively
# encapsulates the crucial points and details from the original content."""

# ## This is the summary, replace this with the actual output from your LLM application
# actual_output="""
# The coverage score quantifies how well a summary captures and
# accurately represents key information from the original text,
# with a higher score indicating greater comprehensiveness."""

prompt = "Summarize the following text: " + input
actual_output=waise_model.invoke(prompt)

test_case = LLMTestCase(input=input, actual_output=actual_output)
metric = SummarizationMetric(
    threshold=0.5,
    model=deepeval_model,
    #     assessment_questions=[
    #     "Is the coverage score based on a percentage of 'yes' answers?",
    #     "Does the score ensure the summary's accuracy with the source?",
    #     "Does a higher score mean a more comprehensive summary?"
    # ]
)

metric.measure(test_case)

print("score: " + str(metric.score))
print("reson:" + metric.reason)

# evaluate test cases in bulk
evaluate([test_case], [metric])
