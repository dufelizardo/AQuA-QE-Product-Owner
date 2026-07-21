from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from .embedding_service import embed

_COLLECTION = "knowledge_methodology"
_VECTOR_SIZE = 1024  # dimensão do bge-m3
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_KNOWLEDGE_DIR = _PROJECT_ROOT / "knowledge" / "methodology"
_STORAGE_PATH = _PROJECT_ROOT / ".data" / "qdrant"


def _client() -> QdrantClient:
    _STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(_STORAGE_PATH))


def _chunk_markdown(caminho: Path) -> list[tuple[str, str]]:
    """Divide um arquivo Markdown em chunks por seção `## `, retornando (texto, fonte)."""
    conteudo = caminho.read_text(encoding="utf-8")
    secoes = conteudo.split("\n## ")
    chunks = []
    for i, secao in enumerate(secoes):
        texto = secao.strip() if i == 0 else f"## {secao}".strip()
        if texto:
            chunks.append((texto, caminho.name))
    return chunks


def index_knowledge(client: QdrantClient | None = None) -> int:
    """Indexa knowledge/methodology/ no Qdrant local e retorna o número de chunks indexados."""
    client = client or _client()
    if not client.collection_exists(_COLLECTION):
        client.create_collection(
            collection_name=_COLLECTION,
            vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
        )

    textos: list[str] = []
    fontes: list[str] = []
    for arquivo in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        for texto, fonte in _chunk_markdown(arquivo):
            textos.append(texto)
            fontes.append(fonte)

    if not textos:
        return 0

    vetores = embed(textos)
    pontos = [
        PointStruct(id=str(uuid4()), vector=vetor, payload={"texto": texto, "fonte": fonte})
        for vetor, texto, fonte in zip(vetores, textos, fontes, strict=True)
    ]
    client.upsert(collection_name=_COLLECTION, points=pontos)
    return len(pontos)


def search(consulta: str, k: int = 5) -> list[str]:
    """Busca os k trechos de knowledge/methodology/ mais relevantes para a consulta."""
    client = _client()
    if not client.collection_exists(_COLLECTION):
        index_knowledge(client=client)
    vetor = embed([consulta])[0]
    resultados = client.query_points(
        collection_name=_COLLECTION, query=vetor, limit=k
    ).points
    return [ponto.payload["texto"] for ponto in resultados]
