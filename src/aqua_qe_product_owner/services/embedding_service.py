import os

import ollama

_DEFAULT_MODEL = "bge-m3"


def _client() -> ollama.Client:
    host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ollama.Client(host=host)


def embed(textos: list[str]) -> list[list[float]]:
    """Gera embeddings para uma lista de textos usando o modelo local de embedding configurado."""
    model = os.getenv("OLLAMA_EMBEDDING_MODEL", _DEFAULT_MODEL)
    resposta = _client().embed(model=model, input=textos)
    return resposta["embeddings"]
