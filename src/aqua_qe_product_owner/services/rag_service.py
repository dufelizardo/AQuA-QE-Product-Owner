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


_COLLECTION_REFINEMENT_MEMORY = "refinement_answer_memory"


def record_refinement_answer(
    pergunta: str, resposta: str, tipo_artefato: str, client: QdrantClient | None = None
) -> None:
    """Grava um par pergunta/resposta de um ciclo de refinamento real, para reaproveitamento
    futuro como sugestão editável (nunca aplicada automaticamente) em ciclos de refinamento
    posteriores — mesmos ou de outros artefatos/projetos."""
    client = client or _client()
    if not client.collection_exists(_COLLECTION_REFINEMENT_MEMORY):
        client.create_collection(
            collection_name=_COLLECTION_REFINEMENT_MEMORY,
            vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
        )
    vetor = embed([pergunta])[0]
    ponto = PointStruct(
        id=str(uuid4()),
        vector=vetor,
        payload={"pergunta": pergunta, "resposta": resposta, "tipo_artefato": tipo_artefato},
    )
    client.upsert(collection_name=_COLLECTION_REFINEMENT_MEMORY, points=[ponto])


def find_similar_refinement_answers(
    pergunta: str, k: int = 1, client: QdrantClient | None = None
) -> list[dict]:
    """Busca as k respostas de refinamento mais parecidas com a pergunta atual (memória
    institucional). Retorna lista vazia se a collection ainda não existir (nenhuma resposta
    registrada até agora) — nunca cria a collection nem indexa nada a partir daqui, diferente
    de `search`, que indexa `knowledge/methodology/` sob demanda (não há conteúdo estático para
    indexar aqui, só o que já foi registrado por `record_refinement_answer`)."""
    client = client or _client()
    if not client.collection_exists(_COLLECTION_REFINEMENT_MEMORY):
        return []
    vetor = embed([pergunta])[0]
    resultados = client.query_points(
        collection_name=_COLLECTION_REFINEMENT_MEMORY, query=vetor, limit=k
    ).points
    return [
        {
            "pergunta": ponto.payload["pergunta"],
            "resposta": ponto.payload["resposta"],
            "tipo_artefato": ponto.payload["tipo_artefato"],
            "score": ponto.score,
        }
        for ponto in resultados
    ]
