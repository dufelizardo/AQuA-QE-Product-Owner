from aqua_qe_product_owner.models import ChatMessage
from aqua_qe_product_owner.skills.parse_chat_transcript import parse_chat_transcript


def test_parses_multiple_speakers():
    texto = "PO: os clientes precisam agendar consulta\nDev: por qual canal?\nPO: so pelo app"

    resultado = parse_chat_transcript(texto)

    assert resultado == [
        ChatMessage(speaker="PO", text="os clientes precisam agendar consulta"),
        ChatMessage(speaker="Dev", text="por qual canal?"),
        ChatMessage(speaker="PO", text="so pelo app"),
    ]


def test_speaker_with_multiple_words():
    texto = "Maria Silva: precisamos revisar o escopo"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="Maria Silva", text="precisamos revisar o escopo")]


def test_continuation_line_attaches_to_previous_speaker():
    texto = "PO: os clientes precisam agendar consulta\ne tambem cancelar consulta ja marcada"

    resultado = parse_chat_transcript(texto)

    assert len(resultado) == 1
    assert resultado[0].speaker == "PO"
    assert resultado[0].text == (
        "os clientes precisam agendar consulta\ne tambem cancelar consulta ja marcada"
    )


def test_plain_text_without_speakers_falls_back_to_single_message():
    texto = "Clientes precisam conseguir contratar CDB pelo app"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="", text=texto)]


def test_colon_mid_sentence_is_not_mistaken_for_a_speaker():
    texto = "O sistema deve responder em: 2 segundos"

    resultado = parse_chat_transcript(texto)

    assert resultado == [ChatMessage(speaker="", text=texto)]


def test_empty_lines_are_ignored():
    texto = "PO: primeira mensagem\n\n\nDev: segunda mensagem"

    resultado = parse_chat_transcript(texto)

    assert resultado == [
        ChatMessage(speaker="PO", text="primeira mensagem"),
        ChatMessage(speaker="Dev", text="segunda mensagem"),
    ]
