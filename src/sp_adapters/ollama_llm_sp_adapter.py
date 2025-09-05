import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")
import src.core.spi.llm_spi as llm_spi
from ollama import chat
from ollama import ChatResponse 
from core.config import OLLAMA_SYSTEM_MESSAGES

class OllamaLLMSPAdapter(llm_spi.LLMSPI):
    """An implementation of the LLMSPI interface for the Ollama LLM provider.

    This adapter allows the retriever and query parser components to invoke
    the Ollama language model using a consistent interface.
    """

    def __init__(self, model: str = "llama3.2") -> None:
        self.model = model

    def invoke_llm(self, prompt: str, system_message: str, **kwargs: any) -> ChatResponse:

        if prompt is None or not isinstance(prompt, str) or prompt.strip() == "":
            raise ValueError("prompt must be a non-empty string")

        response: ChatResponse = chat(model=self.model, messages=[
            {
            'role': 'system',
            'content': system_message,
            },
            {
                "role": "user", 
                "content": prompt
            }
        ])

        return response