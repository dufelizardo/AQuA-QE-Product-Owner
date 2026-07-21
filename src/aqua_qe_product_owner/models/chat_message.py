from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Uma mensagem de uma transcrição de chat, com o remetente quando identificável."""

    speaker: str
    text: str
