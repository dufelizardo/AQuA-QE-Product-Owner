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
from aqua_qe_product_owner.skills.diff_epic_versions import diff_epic_versions  # noqa: E402
from aqua_qe_product_owner.skills.diff_story_versions import diff_story_versions  # noqa: E402
from aqua_qe_product_owner.skills.export_markdown import export_markdown  # noqa: E402
from aqua_qe_product_owner.skills.format_chat_transcript import format_chat_transcript  # noqa: E402
from aqua_qe_product_owner.skills.format_epic_markdown import format_epic_markdown  # noqa: E402
from aqua_qe_product_owner.skills.generate_clarifying_questions import (  # noqa: E402
    generate_clarifying_questions,
)
from aqua_qe_product_owner.skills.generate_traceability_matrix import (  # noqa: E402
    generate_traceability_matrix,
)
from aqua_qe_product_owner.skills.generate_epic_clarifying_questions import (  # noqa: E402
    generate_epic_clarifying_questions,
)
from aqua_qe_product_owner.skills.parse_chat_transcript import parse_chat_transcript  # noqa: E402
from aqua_qe_product_owner.skills.parse_epic_markdown import parse_epic_markdown  # noqa: E402
from aqua_qe_product_owner.skills.parse_story_markdown import parse_story_markdown  # noqa: E402
from aqua_qe_product_owner.skills.read_confluence_page import read_confluence_page  # noqa: E402
from aqua_qe_product_owner.skills.read_jira_issue import read_jira_issue  # noqa: E402
from aqua_qe_product_owner.skills.read_text_file import read_text_file  # noqa: E402
from aqua_qe_product_owner.skills.record_refinement_answer import (  # noqa: E402
    record_refinement_answer,
)
from aqua_qe_product_owner.skills.suggest_refinement_answer import (  # noqa: E402
    suggest_refinement_answer,
)
from aqua_qe_product_owner.skills.update_jira_epic import update_jira_epic  # noqa: E402
from aqua_qe_product_owner.skills.update_jira_issue import update_jira_issue  # noqa: E402
from aqua_qe_product_owner.skills.validate_traceability import validate_traceability  # noqa: E402
from aqua_qe_product_owner.workflow.generate_epic import (  # noqa: E402
    finalize_epic,
    generate_epics_shape,
    generate_epics_stories,
    load_epic_shape,
    refine_epic_shape,
)
from aqua_qe_product_owner.workflow.generate_user_story import finalize_story  # noqa: E402
from aqua_qe_product_owner.workflow.refine_story import refine_user_story  # noqa: E402


def _ler_entrada(args: argparse.Namespace) -> str:
    if args.arquivo:
        return read_text_file(args.arquivo)
    if args.jira:
        return read_jira_issue(args.jira)
    if args.confluence:
        return read_confluence_page(args.confluence)
    # chat (--texto): normaliza a transcrição (remetente por linha), quando houver;
    # texto corrido sem remetentes volta inalterado (ver parse_chat_transcript).
    return format_chat_transcript(parse_chat_transcript(args.texto))


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


_PRIORIDADES = {"1": "Alta", "2": "Média", "3": "Baixa"}


def _perguntar_prioridade(story: UserStory) -> None:
    """Pergunta a prioridade da história ao usuário — o PO decide, o agente nunca sugere (ver knowledge/methodology/dor.md e scrum_guide.md)."""
    print(f"\nPrioridade de '{story.title or story.id}':")
    print("  1) Alta   2) Média   3) Baixa")
    while True:
        escolha = input("Escolha (1/2/3): ").strip()
        if escolha in _PRIORIDADES:
            story.priority = _PRIORIDADES[escolha]
            return
        print("Opção inválida.")


def _ciclo_de_refinamento(story: UserStory) -> UserStory:
    """Gera perguntas, pede respostas ao usuário, refina e reavalia até aprovar ou o usuário desistir."""
    while story.status != StoryStatus.DRAFT_VALIDATED and story.review_notes:
        perguntas = generate_clarifying_questions(story)
        if not perguntas:
            break

        print("\nO revisor apontou problemas. Responda para ajudar a refinar a história:")
        respostas = []
        for pergunta in perguntas:
            sugestao = suggest_refinement_answer(pergunta)
            if sugestao:
                print(
                    f"  \U0001F4A1 Resposta usada antes p/ pergunta parecida "
                    f"(similaridade {sugestao['score']:.2f}): {sugestao['resposta']}"
                )
            resposta = input(f"  {pergunta}\n  > ")
            respostas.append({"pergunta": pergunta, "resposta": resposta})
            if resposta.strip():
                record_refinement_answer(pergunta, resposta, tipo_artefato="story")

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


def _rodar_unitario(
    texto: str,
    saida: str | None,
    jira_key: str | None,
    refinar: bool,
    priorizar: bool = False,
    story_existente: str | None = None,
) -> None:
    if story_existente:
        story = finalize_story(parse_story_markdown(read_text_file(story_existente)))
    else:
        story = handle_request(texto, modo="unitario")
    _imprimir_story(story)

    original = copy.deepcopy(story)
    if refinar:
        story = _ciclo_de_refinamento(story)

    caminho_changelog = f"{saida}.changelog.md" if saida else None
    _processar_aceite(story, original, caminho_changelog, jira_key)

    if story.status == StoryStatus.ACCEPTED and priorizar:
        _perguntar_prioridade(story)

    if saida and story.status == StoryStatus.ACCEPTED:
        export_markdown(story, saida)
        print(f"exportado para: {saida}")


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


def _imprimir_epic_shape(epic: Epic, indice: int | None = None, total: int | None = None) -> None:
    cabecalho = "Épico (escopo definido a partir do PRD, antes de gerar as Stories)"
    if indice is not None and total is not None:
        cabecalho = f"Épico {indice} de {total} — {cabecalho}"
    print(f"\n--- {cabecalho} ---")
    print(f"status: {epic.status.value}")
    print(f"título: {epic.title}")
    print(f"objetivo: {epic.objective}")
    print(f"escopo: {epic.scope}")
    print(f"valor: {epic.value}")
    print(f"requisitos extraídos: {len(epic.requirements)}")

    contexto = epic.prd_context
    if contexto and any(
        [
            contexto.vision,
            contexto.problem,
            contexto.objectives,
            contexto.target_audience,
            contexto.non_functional_requirements,
            contexto.constraints,
            contexto.success_criteria,
            contexto.risks,
            contexto.dependencies,
        ]
    ):
        print("\ncontexto do PRD (além dos requisitos funcionais):")
        if contexto.vision:
            print(f"  visão: {contexto.vision}")
        if contexto.problem:
            print(f"  problema: {contexto.problem}")
        if contexto.objectives:
            print(f"  objetivos: {contexto.objectives}")
        if contexto.target_audience:
            print(f"  público-alvo: {contexto.target_audience}")
        if contexto.non_functional_requirements:
            print(f"  requisitos não funcionais: {contexto.non_functional_requirements}")
        if contexto.constraints:
            print(f"  restrições: {contexto.constraints}")
        if contexto.success_criteria:
            print(f"  critérios de sucesso: {contexto.success_criteria}")
        if contexto.risks:
            print(f"  riscos: {contexto.risks}")
        if contexto.dependencies:
            print(f"  dependências: {contexto.dependencies}")


def _processar_epic_aceito(
    epic: Epic,
    saida: str | None,
    refinar: bool,
    criar_jira: bool,
    epic_original: Epic | None = None,
    jira_epic_key: str | None = None,
    priorizar: bool = False,
    saida_rtm: bool = False,
) -> None:
    """Roda story-by-story a mesma sequência de sempre (imprimir, traceability, refinamento, export, Jira) para um Épico já com as Stories geradas."""
    _imprimir_epic(epic)
    _imprimir_traceability(epic)

    pasta_epic = Path(saida) / epic.id if saida else None

    if refinar:
        if pasta_epic:
            pasta_epic.mkdir(parents=True, exist_ok=True)
        for i, story in enumerate(epic.stories):
            if story.status == StoryStatus.DRAFT_VALIDATED:
                continue
            print(f"\n=== refinando {story.id} ({epic.id}) ===")
            original = copy.deepcopy(story)
            story_refinada = _ciclo_de_refinamento(story)
            epic.stories[i] = story_refinada
            caminho_changelog = (
                str(pasta_epic / f"{story.id}.changelog.md") if pasta_epic else None
            )
            _processar_aceite(story_refinada, original, caminho_changelog, None)

    if priorizar and saida:
        for story in epic.stories:
            _perguntar_prioridade(story)

    if saida:
        pasta_epic.mkdir(parents=True, exist_ok=True)
        for story in epic.stories:
            export_markdown(story, str(pasta_epic / f"{story.id}.md"))
        with open(pasta_epic / f"{epic.id}.md", "w", encoding="utf-8") as arquivo:
            arquivo.write(format_epic_markdown(epic))
        print(f"exportado para: {pasta_epic}/")

        if saida_rtm:
            caminho_rtm = pasta_epic / "RTM.md"
            with open(caminho_rtm, "w", encoding="utf-8") as arquivo:
                arquivo.write(generate_traceability_matrix(epic))
            print(f"matriz de rastreabilidade exportada para: {caminho_rtm}")

    if epic_original is not None:
        diff = diff_epic_versions(epic_original, epic)
        print("\n--- changelog do Épico (antes vs. depois do refinamento) ---")
        print("critérios novos:", diff["criterios_novos"] or "nenhum")
        print("critérios descontinuados:", diff["criterios_descontinuados"] or "nenhum")
        if diff["objetivo_antes"] != diff["objetivo_depois"]:
            print(f"objetivo alterado: '{diff['objetivo_antes']}' -> '{diff['objetivo_depois']}'")
        if diff["escopo_antes"] != diff["escopo_depois"]:
            print(f"escopo alterado: '{diff['escopo_antes']}' -> '{diff['escopo_depois']}'")
        if diff["valor_antes"] != diff["valor_depois"]:
            print(f"valor alterado: '{diff['valor_antes']}' -> '{diff['valor_depois']}'")
        if pasta_epic:
            pasta_epic.mkdir(parents=True, exist_ok=True)
            caminho_changelog = pasta_epic / f"{epic.id}.changelog.md"
            with open(caminho_changelog, "w", encoding="utf-8") as arquivo:
                arquivo.write(f"# Changelog — {epic.id}\n\n")
                arquivo.write(f"## Critérios novos\n{_lista_md_criterios(diff['criterios_novos'])}\n\n")
                arquivo.write(
                    f"## Critérios descontinuados\n{_lista_md_criterios(diff['criterios_descontinuados'])}\n\n"
                )
                arquivo.write(f"## Objetivo\nAntes: {diff['objetivo_antes']}\nDepois: {diff['objetivo_depois']}\n\n")
                arquivo.write(f"## Escopo\nAntes: {diff['escopo_antes']}\nDepois: {diff['escopo_depois']}\n\n")
                arquivo.write(f"## Valor\nAntes: {diff['valor_antes']}\nDepois: {diff['valor_depois']}\n")
            print(f"changelog do Épico exportado para: {caminho_changelog}")

    if jira_epic_key and _perguntar_sim_nao(f"\nPersistir esta versão do Épico no Jira ({jira_epic_key})?"):
        update_jira_epic(jira_epic_key, epic)
        print(f"ticket {jira_epic_key} atualizado no Jira.")

    if criar_jira:
        _criar_epico_no_jira(epic)


def _menu_epic(indice: int, total: int) -> str:
    print(f"\nO que fazer com o Épico {indice} de {total}?")
    print("  1) Gerar as User Stories agora")
    print("  2) Refinar o Épico (título/objetivo/escopo/valor)")
    print("  3) Não continuar com este Épico")
    while True:
        escolha = input("Escolha (1/2/3): ").strip()
        if escolha in ("1", "2", "3"):
            return escolha
        print("Opção inválida.")


def _ciclo_de_refinamento_epic(epic: Epic) -> Epic:
    """Gera perguntas, pede respostas ao usuário, refina e reavalia até aprovar ou o usuário desistir.

    Diferente do PRD/Story, o Épico chega aqui só com o checklist automático
    (validate_epic) aplicado — review_epic (e epic.review_notes) só roda
    dentro de finalize_epic, chamado aqui sob demanda, na entrada deste
    ciclo, para não pagar esse custo de LLM para todo Épico impresso na
    recepção — só para aquele que o usuário escolheu de fato refinar.
    """
    epic = finalize_epic(epic)
    print("\n--- revisão do Épico ---")
    _imprimir_epic_shape(epic)

    while epic.status != StoryStatus.DRAFT_VALIDATED and epic.review_notes:
        perguntas = generate_epic_clarifying_questions(epic)
        if not perguntas:
            break

        print("\nO revisor apontou problemas no Épico. Responda para ajudar a refinar:")
        respostas = []
        for pergunta in perguntas:
            sugestao = suggest_refinement_answer(pergunta)
            if sugestao:
                print(
                    f"  \U0001F4A1 Resposta usada antes p/ pergunta parecida "
                    f"(similaridade {sugestao['score']:.2f}): {sugestao['resposta']}"
                )
            resposta = input(f"  {pergunta}\n  > ")
            respostas.append({"pergunta": pergunta, "resposta": resposta})
            if resposta.strip():
                record_refinement_answer(pergunta, resposta, tipo_artefato="epic")

        epic = refine_epic_shape(epic, respostas)
        print("\n--- Épico refinado ---")
        _imprimir_epic_shape(epic)

        if epic.status != StoryStatus.DRAFT_VALIDATED and not _perguntar_sim_nao(
            "\nTentar refinar de novo?"
        ):
            break
    return epic


def _rodar_lote(
    texto: str,
    saida: str | None,
    refinar: bool,
    criar_jira: bool,
    jira_epic_key: str | None = None,
    priorizar: bool = False,
    saida_rtm: bool = False,
    epic_existente: str | None = None,
) -> None:
    if epic_existente:
        epics = [load_epic_shape(parse_epic_markdown(read_text_file(epic_existente)))]
    else:
        epics = generate_epics_shape(texto)
    total = len(epics)

    # write-back só quando há mapeamento inequívoco 1:1 com o ticket de
    # origem — evita sobrescrever o mesmo ticket com o conteúdo de Épicos
    # diferentes quando o PRD se divide em N grupos (identify_epic_groups).
    permitir_write_back = jira_epic_key is not None and total == 1

    selecionados: list[tuple[Epic, Epic]] = []
    for i, epic in enumerate(epics, start=1):
        _imprimir_epic_shape(epic, indice=i, total=total)
        original = copy.deepcopy(epic)

        while True:
            escolha = _menu_epic(i, total)
            if escolha == "2":
                epic = _ciclo_de_refinamento_epic(epic)
                continue
            if escolha == "3":
                print(f"Épico {i}: descartado a pedido do usuário.")
                break
            selecionados.append((original, epic))
            break

    if not selecionados:
        print("Execução interrompida: nenhuma User Story foi gerada.")
        return

    epics_prontos = generate_epics_stories([atual for _, atual in selecionados])
    for (original, _), epic in zip(selecionados, epics_prontos):
        chave = jira_epic_key if permitir_write_back else None
        _processar_epic_aceito(
            epic,
            saida,
            refinar,
            criar_jira,
            epic_original=original,
            jira_epic_key=chave,
            priorizar=priorizar,
            saida_rtm=saida_rtm,
        )


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
    entrada.add_argument(
        "--epic-existente",
        dest="epic_existente",
        help=(
            "Caminho de um Épico .md já existente (mesmo formato de "
            "format_epic_markdown, exportado como <EPIC-ID>.md) para carregar "
            "e continuar dali — refinar de novo ou gerar as User Stories, em "
            "vez de gerar um Épico novo a partir de um PRD. Só válido com "
            "--modo lote."
        ),
    )
    entrada.add_argument(
        "--story-existente",
        dest="story_existente",
        help=(
            "Caminho de uma User Story .md já existente (mesmo formato de "
            "export_markdown) para carregar e continuar dali — refinar de "
            "novo ou só aceitar, em vez de gerar uma story nova. Só válido "
            "com --modo unitario."
        ),
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
            "não aprovadas, antes do aceite humano (que é sempre perguntado, "
            "com ou sem esta flag)."
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
    parser.add_argument(
        "--priorizar",
        action="store_true",
        help=(
            "Após aceitar a(s) história(s), pergunta a prioridade "
            "(Alta/Média/Baixa) de cada uma — sempre decidida pelo usuário, o "
            "agente nunca sugere (ver knowledge/methodology/dor.md)."
        ),
    )
    parser.add_argument(
        "--saida-rtm",
        action="store_true",
        dest="saida_rtm",
        help=(
            "Modo lote: exporta a Matriz de Rastreabilidade do Épico "
            "(RTM.md, dentro da pasta de --saida) — requisito -> story -> "
            "critérios de aceitação -> status."
        ),
    )
    args = parser.parse_args()

    if args.saida_rtm and args.modo != "lote":
        parser.error("--saida-rtm só é válido com --modo lote.")
    if args.epic_existente and args.modo != "lote":
        parser.error("--epic-existente só é válido com --modo lote.")
    if args.story_existente and args.modo != "unitario":
        parser.error("--story-existente só é válido com --modo unitario.")

    if args.modo == "unitario":
        texto = "" if args.story_existente else _ler_entrada(args)
        _rodar_unitario(
            texto,
            args.saida,
            args.jira,
            args.refinar,
            priorizar=args.priorizar,
            story_existente=args.story_existente,
        )
    else:
        texto = "" if args.epic_existente else _ler_entrada(args)
        _rodar_lote(
            texto,
            args.saida,
            args.refinar,
            args.criar_jira,
            jira_epic_key=args.jira,
            priorizar=args.priorizar,
            saida_rtm=args.saida_rtm,
            epic_existente=args.epic_existente,
        )


if __name__ == "__main__":
    main()
