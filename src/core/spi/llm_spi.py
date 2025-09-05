from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMSPI(ABC):
    """Service Provider Interface (SPI) for LLM providers.

    This defines the port used by the retriever and the query parser components
    to invoke a language model. Implementations should be synchronous and
    return a text response for a given prompt.

    Implementations may accept optional keyword arguments (for example
    `max_tokens` or `temperature`) but are free to ignore unsupported keys.
    """

    @abstractmethod
    def invoke_llm(self, prompt: str, system_message: str, **kwargs: Any) -> str:
        """Invoke the language model with a text prompt.

        Args:
            prompt: The user-facing prompt or instruction to send to the LLM.
            system_message: The system message to include in the request.
            **kwargs: Optional provider-specific options (e.g. max_tokens).

        Returns:
            The text response produced by the LLM.

        Raises:
            ValueError: If the prompt is invalid.
        """
        raise NotImplementedError()


class EchoLLM(LLMSPI):
    """A tiny, deterministic LLM implementation for testing and local use.

    This implementation simply echoes the prompt back with an optional
    prefix. It's safe to use in unit tests and in offline environments.
    """

    def __init__(self, prefix: str = "ECHO:") -> None:
        self.prefix = prefix

    def invoke_llm(self, prompt: str, **kwargs: Any) -> str:
        if prompt is None or not isinstance(prompt, str) or prompt.strip() == "":
            raise ValueError("prompt must be a non-empty string")

        # Provide minimal processing so callers can see deterministic output.
        # Accept but ignore common kwargs to make this drop-in friendly.
        return f"{self.prefix} {prompt.strip()}"


__all__ = ["LLMSPI", "EchoLLM"]
