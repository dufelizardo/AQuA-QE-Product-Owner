from aqua_qe_product_owner.skills import generate_prd as module


def _fake_complete_json(escopo, fora_de_escopo):
    def fake(prompt, system=""):
        return {
            "contexto_problema": "contexto",
            "objetivo": "objetivo",
            "publico_alvo": "publico",
            "escopo": escopo,
            "fora_de_escopo": fora_de_escopo,
            "requisitos_funcionais": ["req 1"],
            "requisitos_nao_funcionais": ["req nf 1"],
            "criterios_sucesso": ["criterio 1"],
            "riscos_premissas": ["risco 1"],
        }

    return fake


def test_generate_prd_com_escopo_como_string(monkeypatch):
    monkeypatch.setattr(
        module, "complete_json", _fake_complete_json("faz X", "não faz Y")
    )

    draft = module.generate_prd("uma ideia")

    assert draft.scope == "faz X"
    assert draft.out_of_scope == "não faz Y"


def test_generate_prd_com_escopo_como_lista_normaliza_para_string(monkeypatch):
    """O LLM às vezes devolve escopo/fora_de_escopo como lista JSON em vez de string; deve virar texto, nunca repr de lista."""
    monkeypatch.setattr(
        module,
        "complete_json",
        _fake_complete_json(["faz X", "faz Z"], ["não faz Y"]),
    )

    draft = module.generate_prd("uma ideia")

    assert draft.scope == "faz X; faz Z"
    assert draft.out_of_scope == "não faz Y"
    assert "[" not in draft.scope
