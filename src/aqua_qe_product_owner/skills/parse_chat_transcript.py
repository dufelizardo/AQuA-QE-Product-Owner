import re

from ..models import ChatMessage

_PADRAO_REMETENTE = re.compile(r"^([A-Za-zÀ-ÿ]+(?:\s[A-Za-zÀ-ÿ]+){0,2}):\s+(.+)$")


def parse_chat_transcript(texto: str) -> list[ChatMessage]:
    """Separa uma transcrição de chat em mensagens por remetente (ex.: "PO: ...", "Dev: ...").

    Puro Python (regex), sem LLM — é reconhecimento de formato, não julgamento
    semântico. O remetente é limitado a 1-3 palavras alfabéticas, para não
    confundir uma frase como "O sistema deve responder em: 2 segundos" com um
    remetente real. Linhas que não batem o padrão viram continuação da
    mensagem do remetente anterior. Se nenhuma linha tiver remetente
    identificável, retorna o texto inteiro como uma única mensagem sem
    remetente — sem alterar nada (mesmo comportamento de hoje para chat que
    já é só um texto corrido).
    """
    mensagens: list[ChatMessage] = []

    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        match = _PADRAO_REMETENTE.match(linha)
        if match:
            mensagens.append(ChatMessage(speaker=match.group(1), text=match.group(2)))
        elif mensagens:
            ultima = mensagens[-1]
            ultima.text = f"{ultima.text}\n{linha}"
        else:
            mensagens.append(ChatMessage(speaker="", text=linha))

    if not mensagens or not any(m.speaker for m in mensagens):
        return [ChatMessage(speaker="", text=texto)]

    return mensagens
