import json
import os

import ollama

_DEFAULT_MODEL = "mistral"


def _client() -> ollama.Client:
    host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ollama.Client(host=host)


def complete(prompt: str, system: str = "", model: str | None = None) -> str:
    """Envia um prompt ao modelo local via Ollama e retorna o texto de resposta."""
    modelo = model or os.getenv("OLLAMA_MODEL", _DEFAULT_MODEL)
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    response = _client().chat(model=modelo, messages=messages)
    return response["message"]["content"]


def complete_json(prompt: str, system: str = "", model: str | None = None) -> dict:
    """Envia um prompt ao modelo local via Ollama e retorna a resposta já parseada como JSON."""
    modelo = model or os.getenv("OLLAMA_MODEL", _DEFAULT_MODEL)
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    response = _client().chat(model=modelo, messages=messages, format="json")
    conteudo = response["message"]["content"]
    try:
        return json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Resposta do LLM não é um JSON válido: {conteudo!r}") from exc
