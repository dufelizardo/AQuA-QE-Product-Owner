"""CLI simples para rodar o AQuA-QE Product Owner sem precisar mexer em sys.path manualmente."""

import argparse
import copy
import sys
from pathlib import Path

from dotenv import load_dotenv

_RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(_RAIZ / "src"))
load_dotenv(_RAIZ / ".env")

from aqua_qe_product_owner.models import Epic, StoryStatus, UserStory  # noqa: E402
from aqua_qe_product_owner.orchestrator.product_owner import handle_request  # noqa: E402
from aqua_qe_product_owner.skills.create_jira_epic import create_jira_epic  # noqa: E402
from aqua_qe_product_owner.skills.create_jira_story import create_jira_story  # noqa: E402
from aqua_qe_product_owner.skills.diff_story_versions import diff_story_versions  # noqa: E402
from aqua_qe_product_owner.skills.export_markdown import export_markdown  # noqa: E402
from aqua_qe_product_owner.skills.generate_clarifying_questions import (  # noqa: E402
    generate_clarifying_questions,
)
from aqua_qe_product_owner.skills.read_confluence_page import read_confluence_page  # noqa: E402
from aqua_qe_product_owner.skills.read_jira_issue import read_jira_issue  # noqa: E402
from aqua_qe_product_owner.skills.read_text_file import read_text_file  # noqa: E402
from aqua_qe_product_owner.skills.update_jira_issue import update_jira_issue  # noqa: E402
from aqua_qe_product_owner.skills.validate_traceability import validate_traceability  # noqa: E402
from aqua_qe_product_owner.workflow.generate_epic import (  # noqa: E402
    generate_epic_shape,
    generate_epic_stories,
)
from aqua_qe_product_owner.workflow.refine_story import refine_user_story  # noqa: E402


def _ler_entrada(args: argparse.Namespace) -> str:
    if args.arquivo:
        return read_text_file(args.arquivo)
    if args.jira:
        return read_jira_issue(args.jira)
    if args.confluence:
        return read_confluence_page(args.confluence)
    return args.texto


def _imprimir_story(story: UserStory) -> None:
    print(f"status: {story.status.value}")
    print(f"ator: {story.actor}")
    print(f"objetivo: {story.goal}")
    if story.review_notes:
        print("observações da revisão:")
        for nota in story.review_notes:
            print(f"  - {nota}")


def _perguntar_sim_nao(mensagem: str) -> bool:
    resposta = input(f"{mensagem} (s/n): ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


def _ciclo_de_refinamento(story: UserStory) -> UserStory:
    """Gera perguntas, pede respostas ao usuário, refina e reavalia até aprovar ou o usuário desistir."""
    while story.status != StoryStatus.DRAFT_VALIDATED and story.review_notes:
        perguntas = generate_clarifying_questions(story)
        if not perguntas:
            break

        print("\nO revisor apontou problemas. Responda para ajudar a refinar a história:")
        respostas = []
        for pergunta in perguntas:
            resposta = input(f"  {pergunta}\n  > ")
            respostas.append({"pergunta": pergunta, "resposta": resposta})

        story = refine_user_story(story, respostas)
        print("\n--- história refinada ---")
        _imprimir_story(story)

        if story.status != StoryStatus.DRAFT_VALIDATED and not _perguntar_sim_nao(
            "\nTentar refinar de novo?"
        ):
            break
    return story


def _lista_md(itens: list[str]) -> str:
    return "\n".join(f"- {item}" for item in itens) if itens else "(nenhuma)"


def _lista_md_criterios(itens: list[tuple[str, str, str]]) -> str:
    if not itens:
        return "(nenhum)"
    return "\n".join(f"- Given {g}, When {w}, Then {t}" for g, w, t in itens)


def _processar_aceite(
    story: UserStory,
    original: UserStory,
    caminho_changelog: str | None,
    jira_key: str | None,
) -> None:
    if not _perguntar_sim_nao("\nAceitar esta história?"):
        return

    story.status = StoryStatus.ACCEPTED
    diff = diff_story_versions(original, story)

    print("\n--- changelog (regras/critérios novos vs. descontinuados) ---")
    print("regras novas:", diff["regras_novas"] or "nenhuma")
    print("regras descontinuadas:", diff["regras_descontinuadas"] or "nenhuma")
    print("critérios novos:", diff["criterios_novos"] or "nenhum")
    print("critérios descontinuados:", diff["criterios_descontinuados"] or "nenhum")

    if caminho_changelog:
        with open(caminho_changelog, "w", encoding="utf-8") as arquivo:
            arquivo.write("# Changelog\n\n")
            arquivo.write(f"## Regras novas\n{_lista_md(diff['regras_novas'])}\n\n")
            arquivo.write(f"## Regras descontinuadas\n{_lista_md(diff['regras_descontinuadas'])}\n\n")
            arquivo.write(f"## Critérios novos\n{_lista_md_criterios(diff['criterios_novos'])}\n\n")
            arquivo.write(
                f"## Critérios descontinuados\n{_lista_md_criterios(diff['criterios_descontinuados'])}\n"
            )
        print(f"changelog exportado para: {caminho_changelog}")

    if jira_key and _perguntar_sim_nao(f"\nPersistir esta versão no Jira ({jira_key})?"):
        update_jira_issue(jira_key, story)
        print(f"ticket {jira_key} atualizado no Jira.")


def _rodar_unitario(texto: str, saida: str | None, jira_key: str | None, refinar: bool) -> None:
    story = handle_request(texto, modo="unitario")
    _imprimir_story(story)

    if refinar:
        original = copy.deepcopy(story)
        story = _ciclo_de_refinamento(story)

    if saida:
        export_markdown(story, saida)
        print(f"exportado para: {saida}")

    if refinar:
        caminho_changelog = f"{saida}.changelog.md" if saida else None
        _processar_aceite(story, original, caminho_changelog, jira_key)


def _imprimir_epic(epic: Epic) -> None:
    print(f"status: {epic.status.value}")
    print(f"título: {epic.title}")
    print(f"objetivo: {epic.objective}")
    print(f"escopo: {epic.scope}")
    print(f"valor: {epic.value}")
    if epic.review_notes:
        print("observações da revisão do Épico:")
        for nota in epic.review_notes:
            print(f"  - {nota}")
    print(f"stories geradas: {len(epic.stories)}")
    for story in epic.stories:
        print(f"  - {story.id} | {story.status.value} | {story.actor} | {story.goal}")
    if epic.unresolved_items:
        print("itens não resolvidos:")
        for item in epic.unresolved_items:
            print(f"  - {item.reason}")


def _imprimir_traceability(epic: Epic) -> None:
    resultado = validate_traceability(epic)
    if not any(resultado.values()):
        print("\ntraceability: nenhuma inconsistência encontrada.")
        return
    print("\ntraceability:")
    if resultado["stories_duplicadas"]:
        print("  stories com objetivo duplicado:")
        for original, duplicada in resultado["stories_duplicadas"]:
            print(f"    - {original} e {duplicada}")
    if resultado["stories_sem_valor"]:
        print("  stories sem benefício (valor de negócio) definido:", resultado["stories_sem_valor"])
    if resultado["requisitos_orfaos"]:
        print("  requisitos não cobertos por nenhuma story:", resultado["requisitos_orfaos"])


def _criar_epico_no_jira(epic: Epic) -> None:
    if not _perguntar_sim_nao("\nAceitar este Épico e criá-lo no Jira (com as stories como filhas)?"):
        return

    epic_key = create_jira_epic(epic)
    print(f"\nÉpico criado no Jira: {epic_key}")
    for story in epic.stories:
        story_key = create_jira_story(story, epic_key)
        print(f"  - {story.id} -> {story_key}")


def _imprimir_epic_shape(epic: Epic) -> None:
    print("\n--- Épico (escopo definido a partir do PRD, antes de gerar as Stories) ---")
    aprovado = epic.status == StoryStatus.DRAFT_VALIDATED
    print(f"checklist automático (validate_epic): {'aprovado' if aprovado else 'reprovado'}")
    print(f"título: {epic.title}")
    print(f"objetivo: {epic.objective}")
    print(f"escopo: {epic.scope}")
    print(f"valor: {epic.value}")
    print(f"requisitos extraídos: {len(epic.requirements)}")


def _rodar_lote(texto: str, saida: str | None, refinar: bool, criar_jira: bool) -> None:
    epic = generate_epic_shape(texto)
    _imprimir_epic_shape(epic)

    if not _perguntar_sim_nao("\nContinuar e gerar as User Stories deste Épico?"):
        print("Execução interrompida: nenhuma User Story foi gerada.")
        return

    epic = generate_epic_stories(epic)
    _imprimir_epic(epic)
    _imprimir_traceability(epic)

    if refinar:
        pasta_saida = Path(saida) if saida else None
        if pasta_saida:
            pasta_saida.mkdir(parents=True, exist_ok=True)
        for i, story in enumerate(epic.stories):
            if story.status == StoryStatus.DRAFT_VALIDATED:
                continue
            print(f"\n=== refinando {story.id} ===")
            original = copy.deepcopy(story)
            story_refinada = _ciclo_de_refinamento(story)
            epic.stories[i] = story_refinada
            caminho_changelog = (
                str(pasta_saida / f"{story.id}.changelog.md") if pasta_saida else None
            )
            _processar_aceite(story_refinada, original, caminho_changelog, None)

    if saida:
        pasta_saida = Path(saida)
        pasta_saida.mkdir(parents=True, exist_ok=True)
        for story in epic.stories:
            export_markdown(story, str(pasta_saida / f"{story.id}.md"))
        print(f"exportado para: {pasta_saida}/")

    if criar_jira:
        _criar_epico_no_jira(epic)


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o AQuA-QE Product Owner.")
    parser.add_argument("--modo", choices=["unitario", "lote"], default="unitario")
    entrada = parser.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--arquivo", help="Caminho de um arquivo .txt/.md de entrada.")
    entrada.add_argument("--texto", help="Texto de entrada direto (chat).")
    entrada.add_argument("--jira", help="Chave do ticket Jira (ex.: PROJ-123).")
    entrada.add_argument(
        "--confluence", help="URL completa ou ID de uma página do Confluence Cloud."
    )
    parser.add_argument(
        "--saida",
        help=(
            "Modo unitario: caminho do .md exportado. "
            "Modo lote: pasta onde cada US-*.md será exportada."
        ),
    )
    parser.add_argument(
        "--refinar",
        action="store_true",
        help=(
            "Ativa o ciclo interativo de perguntas/refinamento para histórias "
            "não aprovadas, com prompt final de aceitação e changelog."
        ),
    )
    parser.add_argument(
        "--criar-jira",
        action="store_true",
        dest="criar_jira",
        help=(
            "Modo lote: após gerar o Épico, pergunta se deve aceitá-lo e criá-lo "
            "no Jira (JIRA_PROJECT_KEY), com as User Stories como tickets filhos."
        ),
    )
    args = parser.parse_args()

    texto = _ler_entrada(args)
    if args.modo == "unitario":
        _rodar_unitario(texto, args.saida, args.jira, args.refinar)
    else:
        _rodar_lote(texto, args.saida, args.refinar, args.criar_jira)


if __name__ == "__main__":
    main()
