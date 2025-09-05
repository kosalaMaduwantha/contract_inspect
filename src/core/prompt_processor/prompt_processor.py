
"""Module-level holder for a pluggable LLM service provider adapter.

Call `init(adapter)` once at startup to set the adapter. Other functions in
this module should call `get_llm_adapter()` to obtain the adapter; that
function raises a clear error if the adapter was not initialized.
"""

from typing import Any, Optional
import logging
# Module-level variable. Use get_llm_adapter() to access safely.
llm_sp_adapter: Optional[Any] = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def init(llm_adapter: Any) -> None:
    """Initialize the module-level LLM adapter.

    Args:
        llm_adapter: An object that implements the expected LLM interface
                     (must provide an `invoke_llm(prompt, **kwargs)` method).
    """
    global llm_sp_adapter
    llm_sp_adapter = llm_adapter

def get_llm_adapter() -> Any:
    """Return the initialized LLM adapter or raise RuntimeError if missing."""
    if llm_sp_adapter is None:
        raise RuntimeError("LLM adapter not initialized. Call init(adapter) first.")
    return llm_sp_adapter

def clear_llm_adapter() -> None:
    """Clear the module-level adapter (useful for tests)."""
    global llm_sp_adapter
    llm_sp_adapter = None
    
def _invoke_llm_and_get_content(prompt: str, system_message: str=None) -> str:
    """Helper to invoke LLM and return the content from the response."""
    llm_adapter = get_llm_adapter()
    response = llm_adapter.invoke_llm(prompt=prompt, system_message=system_message)
    return response['message']['content']

def extract_entities(prompt: str, system_message: str) -> str:
    """Extract entities from the given prompt using the LLM adapter."""
    logger.debug("extract_entities called with prompt: %s", prompt)
    return _invoke_llm_and_get_content(prompt, system_message)

def create_query_context(passages: list[str], query: str, instructions: str) -> str:
    """
    Construct a prompt for RAG using plain text passages and clear instructions.

    Args:
        passages: A list of passage strings.
        query: The user query to append to the context.
        instructions: Instructional text to prepend to the prompt.

    Returns:
        A formatted string combining the passages and the user query, suitable for LLM input.
    """
    context_lines = ["Passages:"]
    if not passages:
        context_lines.append("(no passages found)")
    else:
        for i, text in enumerate(passages, 1):
            context_lines.append(f"{i}. {text.strip()}")
    context = "\n".join(context_lines)
    prompt = f"{instructions}\n{context}\n\nUser Query:\n{query}"
    return prompt

def generate_answer(prompt: str) -> str:
    """Generate an answer from the given prompt using the LLM adapter.

    Args:
        prompt: The user-facing prompt or instruction to send to the LLM.
        system_message: The system message to include in the request.

    Returns:
        The text response produced by the LLM.
    """
    """Generate an answer from the given prompt using the LLM adapter."""
    logger.debug("generate_answer called with prompt: %s", prompt)
    return _invoke_llm_and_get_content(prompt)
