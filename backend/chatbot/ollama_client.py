import ollama
from typing import List, Dict

def query_ollama(system_prompt: str, user_prompt: str, model: str = "phi3:mini") -> str:
    """
    Query Ollama with a system-level instruction and user prompt.
    Returns assistant text (string).
    """
    try:
        # Use role-based messages (system first)
        resp = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        # Ollama response structure: resp["message"]["content"]
        return resp["message"]["content"]
    except Exception as e:
        # Wrap exception to make debugging easier upstream
        raise RuntimeError(f"Ollama call failed: {e}")


def classify_intent_with_ollama(system_prompt: str, user_prompt: str, model: str = "phi3:mini") -> str:
    """
    Helper function if you want a raw classification response from Ollama.
    Returns assistant string (could be JSON or human-text depending on your prompt).
    """
    return query_ollama(system_prompt, user_prompt, model=model)
