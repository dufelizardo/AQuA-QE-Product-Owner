import os

import httpx


def _credenciais() -> tuple[str, str, str]:
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")
    email = os.environ["JIRA_EMAIL"]
    token = os.environ["JIRA_API_TOKEN"]
    return base_url, email, token


def _adf_para_texto(node: dict | None) -> str:
    """Extrai texto simples de um nó no formato Atlassian Document Format (ADF)."""
    if not node:
        return ""
    if node.get("type") == "text":
        return node.get("text", "")

    partes = [_adf_para_texto(filho) for filho in node.get("content", [])]
    texto = " ".join(parte for parte in partes if parte)
    if node.get("type") in ("paragraph", "heading"):
        return texto + "\n"
    return texto


def _texto_para_adf(texto: str) -> dict:
    """Converte texto simples em um documento Atlassian Document Format (ADF), um parágrafo por linha não vazia."""
    paragrafos = [
        {"type": "paragraph", "content": [{"type": "text", "text": linha}]}
        for linha in texto.splitlines()
        if linha.strip()
    ]
    return {"type": "doc", "version": 1, "content": paragrafos}


def get_issue_text(issue_key: str) -> str:
    """Busca um ticket no Jira Cloud e retorna resumo + descrição como texto simples."""
    base_url, email, token = _credenciais()

    resposta = httpx.get(
        f"{base_url}/rest/api/3/issue/{issue_key}",
        auth=(email, token),
        params={"fields": "summary,description"},
        timeout=30,
    )
    resposta.raise_for_status()
    campos = resposta.json()["fields"]

    resumo = campos.get("summary", "")
    descricao = _adf_para_texto(campos.get("description"))
    return f"{resumo}\n\n{descricao}".strip()


def update_issue_description(issue_key: str, texto: str) -> None:
    """Atualiza a descrição de um ticket no Jira Cloud a partir de texto simples."""
    base_url, email, token = _credenciais()

    resposta = httpx.put(
        f"{base_url}/rest/api/3/issue/{issue_key}",
        auth=(email, token),
        json={"fields": {"description": _texto_para_adf(texto)}},
        timeout=30,
    )
    resposta.raise_for_status()


def create_issue(
    project_key: str,
    issue_type_id: str,
    summary: str,
    texto: str,
    parent_key: str | None = None,
) -> str:
    """Cria um novo ticket no Jira Cloud e retorna a chave gerada (ex.: PROJ-42)."""
    base_url, email, token = _credenciais()

    fields = {
        "project": {"key": project_key},
        "issuetype": {"id": issue_type_id},
        "summary": summary,
        "description": _texto_para_adf(texto),
    }
    if parent_key:
        fields["parent"] = {"key": parent_key}

    resposta = httpx.post(
        f"{base_url}/rest/api/3/issue",
        auth=(email, token),
        json={"fields": fields},
        timeout=30,
    )
    resposta.raise_for_status()
    return resposta.json()["key"]
