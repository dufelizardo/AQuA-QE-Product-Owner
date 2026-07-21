from ..models import ChatMessage


def format_chat_transcript(mensagens: list[ChatMessage]) -> str:
    """Reconstrói uma transcrição normalizada ("Remetente: mensagem" por parágrafo) a partir das mensagens.

    Puro Python, determinístico — mesma natureza de format_prd_markdown. Para
    o caso de uma única mensagem sem remetente (fallback de
    parse_chat_transcript, quando a entrada não é uma transcrição de
    verdade), retorna o texto original sem nenhuma alteração — zero
    regressão para chat que hoje já é só uma ideia em texto corrido.
    """
    if not mensagens:
        return ""
    if len(mensagens) == 1 and not mensagens[0].speaker:
        return mensagens[0].text

    return "\n\n".join(
        f"{m.speaker}: {m.text}" if m.speaker else m.text for m in mensagens
    )
