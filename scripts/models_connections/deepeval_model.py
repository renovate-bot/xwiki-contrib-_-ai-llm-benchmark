import asyncio
from deepeval.models.base_model import DeepEvalBaseLLM

class EvaluatorModel(DeepEvalBaseLLM):
    def __init__(
        self,
        model
    ):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        return chat_model.invoke(prompt)

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        # Run the synchronous invoke method in a separate thread
        res = await asyncio.to_thread(chat_model.invoke, prompt)
        return res

    def get_model_name(self):
        return "Custom waise model: [{}]".format(self.model.model)
    
class OllamaModel(DeepEvalBaseLLM):
    def __init__(
        self,
        model
    ):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        return chat_model.invoke(prompt)

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        return res

    def get_model_name(self):
        return "Custom ollama model: [{}]".format(self.model.model)

####    
## Examples:
# 1) Custom model
# waise_model = CustomModel(model=WaiseModel(model="AI.Models.mixtral_plain", temperature=0.7, stream=False, verbose=False))

# 2) Ollama model
# ollama_model = OllamaModel(model=Ollama(model="mixtral"))