import re

from ..models import AcceptanceCriteria, BusinessRule, UserStory

_ID_RE = re.compile(r"\*\*ID\*\*:\s*(.+)")
_TITULO_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_PRIORIDADE_RE = re.compile(r"\*\*Prioridade\*\*:\s*(.+)")
_ATOR_RE = re.compile(r"^Como (.+),$", re.MULTILINE)
_OBJETIVO_RE = re.compile(r"^Quero (.+),$", re.MULTILINE)
_BENEFICIO_RE = re.compile(r"^Para que (.+)\.$", re.MULTILINE)
_REGRA_RE = re.compile(r"-\s*\*\*(.+?)\*\*:\s*(.+)")
_RASTREABILIDADE_RE = re.compile(r"^>\s*(.*)$", re.MULTILINE)


def _parse_regras(bloco: str, fonte: str) -> list[BusinessRule]:
    regras = []
    for linha in bloco.splitlines():
        m = _REGRA_RE.match(linha.strip())
        if m:
            regras.append(
                BusinessRule(id=m.group(1).strip(), description=m.group(2).strip(), source_reference=fonte)
            )
    return regras


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


def _parse_lista(bloco: str) -> list[str]:
    return [
        linha.strip()[2:].strip()
        for linha in bloco.splitlines()
        if linha.strip().startswith("- ")
    ]


def parse_story_markdown(texto: str) -> UserStory:
    """Reconstrói uma UserStory a partir do Markdown de export_markdown, preservando a redação original campo a campo.

    Puro Python, determinístico — nunca invoca o LLM. `status`/`review_notes`
    não são restaurados do arquivo — ficam para `finalize_story` recalcular,
    mesma decisão já tomada em `parse_epic_markdown`. IDs de critério de
    aceitação são regenerados sequencialmente; regras de negócio usam o
    `source_reference` da própria story como fallback, já que
    `export_markdown` não exporta a origem de cada regra individualmente.
    """
    secoes = re.split(r"(?m)^## (.+)$", texto)
    preambulo = secoes[0]
    mapa = {titulo.strip(): conteudo for titulo, conteudo in zip(secoes[1::2], secoes[2::2])}

    id_match = _ID_RE.search(preambulo)
    titulo_match = _TITULO_RE.search(preambulo)
    prioridade_match = _PRIORIDADE_RE.search(preambulo)

    descricao_bloco = mapa.get("Descrição", "")
    ator_match = _ATOR_RE.search(descricao_bloco)
    objetivo_match = _OBJETIVO_RE.search(descricao_bloco)
    beneficio_match = _BENEFICIO_RE.search(descricao_bloco)
    linhas_descricao = [
        linha
        for linha in descricao_bloco.splitlines()
        if linha.strip() and not linha.strip().startswith(("Como ", "Quero ", "Para que "))
    ]
    descricao = "\n".join(linhas_descricao).strip()

    fonte_match = _RASTREABILIDADE_RE.search(mapa.get("Rastreabilidade", ""))
    fonte = fonte_match.group(1).strip() if fonte_match else ""

    return UserStory(
        id=id_match.group(1).strip() if id_match else "US-001",
        title=titulo_match.group(1).strip() if titulo_match else "",
        actor=ator_match.group(1).strip() if ator_match else "",
        goal=objetivo_match.group(1).strip() if objetivo_match else "",
        benefit=beneficio_match.group(1).strip() if beneficio_match else "",
        description=descricao,
        acceptance_criteria=_parse_criterios(mapa.get("Critérios de Aceitação", "")),
        business_rules=_parse_regras(mapa.get("Regras de Negócio", ""), fonte),
        assumptions=_parse_lista(mapa.get("Suposições", "")),
        dependencies=_parse_lista(mapa.get("Dependências", "")),
        source_reference=fonte,
        priority=prioridade_match.group(1).strip() if prioridade_match else None,
    )
