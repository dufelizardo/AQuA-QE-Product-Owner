import html
import os
from html.parser import HTMLParser

import httpx


def _credenciais() -> tuple[str, str, str]:
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")
    email = os.environ["JIRA_EMAIL"]
    token = os.environ["JIRA_API_TOKEN"]
    return base_url, email, token


class _StorageFormatParaTexto(HTMLParser):
    """Extrai texto simples do storage format (XHTML) do Confluence, quebrando linha em tags de bloco."""

    _TAGS_DE_QUEBRA = {"p", "li", "h1", "h2", "h3", "h4", "h5", "tr", "br", "hr"}

    def __init__(self) -> None:
        super().__init__()
        self._linhas: list[str] = []
        self._atual: list[str] = []

    def handle_data(self, data: str) -> None:
        self._atual.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in self._TAGS_DE_QUEBRA:
            texto = "".join(self._atual).strip()
            if texto:
                self._linhas.append(texto)
            self._atual = []

    def texto(self) -> str:
        restante = "".join(self._atual).strip()
        if restante:
            self._linhas.append(restante)
        return "\n".join(self._linhas)


def _storage_para_texto(storage_html: str) -> str:
    """Converte o storage format (XHTML) de uma página do Confluence em texto simples."""
    parser = _StorageFormatParaTexto()
    parser.feed(storage_html)
    return parser.texto()


def _texto_para_storage(texto: str) -> str:
    """Converte texto simples no storage format (XHTML) do Confluence, um parágrafo por linha não vazia."""
    paragrafos = [
        f"<p>{html.escape(linha)}</p>" for linha in texto.splitlines() if linha.strip()
    ]
    return "".join(paragrafos)


def create_page(
    space_key: str, title: str, texto: str, parent_page_id: str | None = None
) -> str:
    """Cria uma nova página no Confluence Cloud a partir de texto simples e retorna o id da página criada."""
    base_url, email, token = _credenciais()

    body: dict = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"value": _texto_para_storage(texto), "representation": "storage"}},
    }
    if parent_page_id:
        body["ancestors"] = [{"id": parent_page_id}]

    resposta = httpx.post(
        f"{base_url}/wiki/rest/api/content",
        auth=(email, token),
        json=body,
        timeout=30,
    )
    resposta.raise_for_status()
    return resposta.json()["id"]


def get_page_text(page_id: str) -> str:
    """Busca uma página no Confluence Cloud e retorna título + corpo como texto simples."""
    base_url, email, token = _credenciais()

    resposta = httpx.get(
        f"{base_url}/wiki/rest/api/content/{page_id}",
        auth=(email, token),
        params={"expand": "body.storage"},
        timeout=30,
    )
    resposta.raise_for_status()
    dados = resposta.json()

    titulo = dados.get("title", "")
    corpo = _storage_para_texto(dados.get("body", {}).get("storage", {}).get("value", ""))
    return f"{titulo}\n\n{corpo}".strip()
