import html
import os
import re
from html.parser import HTMLParser

import httpx

_NEGRITO_RE = re.compile(r"\*\*(.+?)\*\*")
_ITEM_NUMERADO_RE = re.compile(r"^\d+\.\s+")
_SEPARADOR_TABELA_RE = re.compile(r"^\|(?:[\s:-]+\|)+$")


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


def _inline(texto: str) -> str:
    """Escapa o texto para HTML e converte **negrito** Markdown em <strong> (única marcação inline suportada)."""
    return _NEGRITO_RE.sub(r"<strong>\1</strong>", html.escape(texto))


def _celulas_tabela(linha: str) -> list[str]:
    return [celula.strip() for celula in linha.strip().strip("|").split("|")]


def _tabela_para_storage(linhas: list[str]) -> str:
    """Converte linhas '| a | b |' (primeira linha = cabeçalho, separador já removido) numa tabela HTML."""
    cabecalho, *corpo = linhas
    linha_cabecalho = (
        "<tr>" + "".join(f"<th>{_inline(c)}</th>" for c in _celulas_tabela(cabecalho)) + "</tr>"
    )
    linhas_corpo = [
        "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in _celulas_tabela(linha)) + "</tr>"
        for linha in corpo
    ]
    return "<table><tbody>" + linha_cabecalho + "".join(linhas_corpo) + "</tbody></table>"


def _texto_para_storage(texto: str) -> str:
    """Converte um subconjunto de Markdown (#/##/###, listas com "- "/"1. ", tabelas e **negrito**)
    no storage format (XHTML) do Confluence.

    Usado para publicar o PRD (produzido por format_prd_markdown), sempre Markdown. Cobre só
    o que esse formatador efetivamente gera — não é um conversor Markdown genérico.
    """
    partes: list[str] = []
    itens_lista: list[str] = []
    tipo_lista: str | None = None  # "ul" ou "ol"
    linhas_tabela: list[str] = []

    def fechar_lista() -> None:
        nonlocal tipo_lista
        if itens_lista:
            tag = tipo_lista or "ul"
            partes.append(f"<{tag}>" + "".join(f"<li>{item}</li>" for item in itens_lista) + f"</{tag}>")
            itens_lista.clear()
        tipo_lista = None

    def fechar_tabela() -> None:
        if linhas_tabela:
            partes.append(_tabela_para_storage(list(linhas_tabela)))
            linhas_tabela.clear()

    linhas = [linha.strip() for linha in texto.splitlines()]
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        if not linha:
            i += 1
            continue

        if (
            not linhas_tabela
            and linha.startswith("|")
            and i + 1 < len(linhas)
            and _SEPARADOR_TABELA_RE.match(linhas[i + 1])
        ):
            fechar_lista()
            linhas_tabela.append(linha)
            i += 1
            continue

        if linhas_tabela:
            if linha.startswith("|"):
                if not _SEPARADOR_TABELA_RE.match(linha):
                    linhas_tabela.append(linha)
                i += 1
                continue
            fechar_tabela()

        if linha.startswith("### "):
            fechar_lista()
            partes.append(f"<h3>{_inline(linha[4:])}</h3>")
        elif linha.startswith("## "):
            fechar_lista()
            partes.append(f"<h2>{_inline(linha[3:])}</h2>")
        elif linha.startswith("# "):
            fechar_lista()
            partes.append(f"<h1>{_inline(linha[2:])}</h1>")
        elif linha.startswith("- "):
            if tipo_lista == "ol":
                fechar_lista()
            tipo_lista = "ul"
            itens_lista.append(_inline(linha[2:]))
        elif _ITEM_NUMERADO_RE.match(linha):
            if tipo_lista == "ul":
                fechar_lista()
            tipo_lista = "ol"
            itens_lista.append(_inline(_ITEM_NUMERADO_RE.sub("", linha)))
        else:
            fechar_lista()
            partes.append(f"<p>{_inline(linha)}</p>")
        i += 1

    fechar_lista()
    fechar_tabela()
    return "".join(partes)


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


def update_page(page_id: str, texto: str) -> None:
    """Atualiza o corpo de uma página existente no Confluence Cloud a partir de texto simples, mantendo título e id."""
    base_url, email, token = _credenciais()

    atual = httpx.get(
        f"{base_url}/wiki/rest/api/content/{page_id}",
        auth=(email, token),
        params={"expand": "version"},
        timeout=30,
    )
    atual.raise_for_status()
    dados = atual.json()

    resposta = httpx.put(
        f"{base_url}/wiki/rest/api/content/{page_id}",
        auth=(email, token),
        json={
            "id": page_id,
            "type": "page",
            "title": dados["title"],
            "version": {"number": dados["version"]["number"] + 1},
            "body": {
                "storage": {"value": _texto_para_storage(texto), "representation": "storage"}
            },
        },
        timeout=30,
    )
    resposta.raise_for_status()


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
