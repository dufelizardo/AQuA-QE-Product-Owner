import re

from ..models import AcceptanceCriteria, Epic, Requirement

_ID_RE = re.compile(r"\*\*ID\*\*:\s*(.+)")
_TITULO_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _parse_requisitos(bloco: str) -> list[Requirement]:
    linhas = [linha for linha in bloco.splitlines() if linha.strip()]
    requisitos = []
    contador = 0
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        if linha.startswith("- "):
            contador += 1
            texto = linha[2:].strip()
            fonte = texto
            if i + 1 < len(linhas) and linhas[i + 1].strip().startswith(">"):
                fonte = linhas[i + 1].strip()[1:].strip()
                i += 1
            requisitos.append(
                Requirement(id=f"REQ-{contador:03d}", text=texto, source_reference=fonte)
            )
        i += 1
    return requisitos


def _parse_criterios(bloco: str) -> list[AcceptanceCriteria]:
    partes = re.split(r"(?m)^### (.+)$", bloco)
    criterios = []
    for i, (cenario, conteudo) in enumerate(zip(partes[1::2], partes[2::2]), start=1):
        given = re.search(r"(?m)^- Given (.+)$", conteudo)
        when = re.search(r"(?m)^- When (.+)$", conteudo)
        then = re.search(r"(?m)^- Then (.+)$", conteudo)
        criterios.append(
            AcceptanceCriteria(
                id=f"AC-{i:03d}",
                scenario=cenario.strip(),
                given=given.group(1).strip() if given else "",
                when=when.group(1).strip() if when else "",
                then=then.group(1).strip() if then else "",
            )
        )
    return criterios


def parse_epic_markdown(texto: str) -> Epic:
    """Reconstrói um Epic (estágio shape) a partir do Markdown de format_epic_markdown, preservando a redação original campo a campo.

    Puro Python, determinístico — nunca invoca o LLM. IDs de requisito/
    critério são regenerados sequencialmente (REQ-001..., AC-001...), não
    preservados do arquivo — evita colisão/gaps se o arquivo for editado
    manualmente.
    """
    id_match = _ID_RE.search(texto)
    titulo_match = _TITULO_RE.search(texto)

    secoes = re.split(r"(?m)^## (.+)$", texto)
    mapa = {titulo.strip(): conteudo for titulo, conteudo in zip(secoes[1::2], secoes[2::2])}

    return Epic(
        id=id_match.group(1).strip() if id_match else "EPIC-001",
        title=titulo_match.group(1).strip() if titulo_match else "",
        objective=mapa.get("Objetivo", "").strip(),
        scope=mapa.get("Escopo", "").strip(),
        value=mapa.get("Valor", "").strip(),
        requirements=_parse_requisitos(mapa.get("Requisitos", "")),
        acceptance_criteria=_parse_criterios(mapa.get("Critérios de Aceitação", "")),
    )
