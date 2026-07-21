from aqua_qe_product_owner.models import ChatMessage
from aqua_qe_product_owner.skills.format_chat_transcript import format_chat_transcript


def test_formats_multiple_messages_with_speaker_prefix():
    mensagens = [
        ChatMessage(speaker="PO", text="os clientes precisam agendar consulta"),
        ChatMessage(speaker="Dev", text="por qual canal?"),
    ]

    resultado = format_chat_transcript(mensagens)

    assert resultado == "PO: os clientes precisam agendar consulta\n\nDev: por qual canal?"


def test_single_unattributed_message_returns_original_text_unchanged():
    texto_original = "Clientes precisam conseguir contratar CDB pelo app"

    resultado = format_chat_transcript([ChatMessage(speaker="", text=texto_original)])

    assert resultado == texto_original


def test_empty_list_returns_empty_string():
    assert format_chat_transcript([]) == ""


def test_roundtrip_parse_then_format_preserves_plain_text():
    from aqua_qe_product_owner.skills.parse_chat_transcript import parse_chat_transcript

    texto_original = "O sistema deve responder em: 2 segundos"

    resultado = format_chat_transcript(parse_chat_transcript(texto_original))

    assert resultado == texto_original
