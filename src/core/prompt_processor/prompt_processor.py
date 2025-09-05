
"""Module-level holder for a pluggable LLM service provider adapter.

Call `init(adapter)` once at startup to set the adapter. Other functions in
this module should call `get_llm_adapter()` to obtain the adapter; that
function raises a clear error if the adapter was not initialized.
"""

from typing import Any, Optional
# Module-level variable. Use get_llm_adapter() to access safely.
llm_sp_adapter: Optional[Any] = None


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
    
def extract_entities(prompt: str, system_message: str) -> str:
    """Extract entities from the given prompt using the LLM adapter.

    Args:
        prompt: The user-facing prompt or instruction to send to the LLM.
        system_message: The system message to include in the request.

    Returns:
        The text response produced by the LLM.
    """
    llm_adapter = get_llm_adapter()
    entities = llm_adapter.invoke_llm(prompt=prompt, system_message=system_message)
    return entities['message']['content']

def create_query_context(passages: list, query: str, max_tokens: int = 2048) -> str:
    """Construct a context string from passages and a user query.

    Args:
        passages: A list of text passages to include in the context.
        query: The user query to append to the context.
        max_tokens: Optional maximum token limit for the combined context.

    Returns:
        A single string combining the passages and the user query.
    """
    context = "\n---\n".join(passages)
    prompt = f"{context}\n\n---\nUser Query: {query}"
    # Optionally truncate prompt to max_tokens if needed
    return prompt
