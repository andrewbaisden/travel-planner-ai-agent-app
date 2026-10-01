"""Shared language-model adapter for Ollama and Groq via Agno.

Gradio and FastAPI both call this module. Ollama is the default. Groq models
are listed and used only when GROQ_API_KEY is set. Their names keep a
``groq:`` prefix so the same ``model_name`` field can route either provider.
"""

import logging
import os
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)

GROQ_PREFIX = "groq:"
FALLBACK_OLLAMA_MODELS = ["llama3", "mistral", "gemma", "phi3"]
FALLBACK_GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
]


def groq_api_key() -> str:
    return os.getenv("GROQ_API_KEY", "").strip()


def is_groq_model(model_name: str) -> bool:
    return model_name.startswith(GROQ_PREFIX)


def groq_model_id(model_name: str) -> str:
    return model_name[len(GROQ_PREFIX):]


def _groq_client_kwargs() -> dict:
    kwargs = {"api_key": groq_api_key()}
    base_url = os.getenv("GROQ_BASE_URL", "").strip()
    if base_url:
        kwargs["base_url"] = base_url
    return kwargs


def _is_chat_model(model_id: str) -> bool:
    skipped = ("whisper", "prompt-guard", "orpheus")
    return not any(part in model_id for part in skipped)


def parse_ollama_list(response: Any) -> List[str]:
    """Turn an ``ollama.list()`` result into bare model names."""
    available: List[str] = []

    if hasattr(response, "models") and isinstance(response.models, list):
        for model in response.models:
            if hasattr(model, "model"):
                model_name = str(model.model)
                if model_name.endswith(":latest"):
                    model_name = model_name.replace(":latest", "")
                available.append(model_name)
    elif isinstance(response, dict) and "models" in response:
        for model in response["models"]:
            if "name" in model:
                model_name = str(model["name"])
                if model_name.endswith(":latest"):
                    model_name = model_name.replace(":latest", "")
                available.append(model_name)

    return available


def list_ollama_models() -> List[str]:
    import ollama

    return parse_ollama_list(ollama.list())


def list_groq_models() -> List[str]:
    if not groq_api_key():
        return []

    try:
        from groq import Groq

        client = Groq(**_groq_client_kwargs())
        listed = client.models.list()
        data = getattr(listed, "data", None) or []
        names: List[str] = []
        for model in data:
            if isinstance(model, dict):
                model_id = model.get("id")
            else:
                model_id = getattr(model, "id", None)
            if not model_id or not _is_chat_model(str(model_id)):
                continue
            names.append(f"{GROQ_PREFIX}{model_id}")
        if names:
            return names
    except Exception as exc:
        logger.warning("Could not list Groq models: %s", exc)

    return [f"{GROQ_PREFIX}{model_id}" for model_id in FALLBACK_GROQ_MODELS]


def list_models() -> List[str]:
    ollama_models: List[str] = []
    try:
        ollama_models = list_ollama_models()
    except Exception as exc:
        logger.error("Error getting Ollama models: %s", exc)

    groq_models = list_groq_models()
    if ollama_models or groq_models:
        return ollama_models + groq_models
    return list(FALLBACK_OLLAMA_MODELS)


def _response_text(result: Any) -> str:
    content = getattr(result, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
            else:
                text = getattr(item, "text", None)
                if text:
                    parts.append(str(text))
        return "\n".join(parts)
    if isinstance(result, dict) and isinstance(result.get("content"), str):
        return result["content"]
    return ""


class SimpleOllamaAgent:
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        logger.info("Initializing SimpleOllamaAgent with model: %s", model_name)

    def run(self, prompt: str) -> str:
        import ollama

        try:
            logger.info("Generating with Ollama model: %s", self.model_name)
            response = ollama.generate(model=self.model_name, prompt=prompt)
            if isinstance(response, dict):
                return response["response"]
            return response.response
        except Exception as exc:
            logger.error("Error generating with Ollama: %s", exc)
            return "I'm sorry, I couldn't generate a response. Please try again."


class GroqAgnoAgent:
    """One Agno agent backed by Groq. TravelAgent still owns phase memory."""

    def __init__(self, model_id: str):
        self.model_name = model_id
        logger.info("Initializing GroqAgnoAgent with model: %s", model_id)

    def run(self, prompt: str) -> str:
        from agno.agent import Agent
        from agno.models.groq import Groq

        try:
            logger.info("Generating with Agno Groq model: %s", self.model_name)
            model_kwargs = {"id": self.model_name, "api_key": groq_api_key()}
            base_url = os.getenv("GROQ_BASE_URL", "").strip()
            if base_url:
                model_kwargs["base_url"] = base_url

            agent = Agent(model=Groq(**model_kwargs), markdown=True)
            text = _response_text(agent.run(prompt))
            if text.strip():
                return text
            return "I'm sorry, I couldn't generate a response. Please try again."
        except Exception as exc:
            logger.error("Error generating with Groq: %s", exc)
            return "I'm sorry, I couldn't generate a response. Please try again."


def resolve_model_name(model_name: str) -> str:
    """Return a model this process can call.

    A ``groq:`` name is kept when a key is set. An Ollama name falls back to
    the first installed model when the requested one is missing.
    """
    if is_groq_model(model_name):
        if not groq_api_key():
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to .env or choose an Ollama model."
            )
        return model_name

    try:
        available = list_ollama_models()
    except Exception as exc:
        raise RuntimeError(f"Error with Ollama: {exc}") from exc

    if model_name in available:
        return model_name
    if available:
        logger.warning(
            "Requested model %s not found. Using %s", model_name, available[0]
        )
        return available[0]

    raise RuntimeError(
        "No models available in Ollama. Please run 'ollama pull llama3' to download a model."
    )


def create_language_model(model_name: str = "llama3"):
    resolved = resolve_model_name(model_name)
    if is_groq_model(resolved):
        return GroqAgnoAgent(groq_model_id(resolved))
    return SimpleOllamaAgent(model_name=resolved)
