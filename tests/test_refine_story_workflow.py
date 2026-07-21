from aqua_qe_product_owner.models import StoryStatus, UserStory
from aqua_qe_product_owner.workflow import refine_story as module


def test_refine_user_story_calls_skill_then_finalizes(monkeypatch):
    story = UserStory(
        id="US-001",
        title="titulo",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao",
        source_reference="fonte",
    )
    respostas = [{"pergunta": "P?", "resposta": "R."}]

    captured = {}

    def fake_refine_story(story_recebida, respostas_recebidas):
        captured["story"] = story_recebida
        captured["respostas"] = respostas_recebidas
        story_recebida.description = "descricao refinada"
        return story_recebida

    def fake_finalize_story(story_recebida):
        story_recebida.status = StoryStatus.DRAFT_VALIDATED
        return story_recebida

    monkeypatch.setattr(module, "refine_story", fake_refine_story)
    monkeypatch.setattr(module, "finalize_story", fake_finalize_story)

    resultado = module.refine_user_story(story, respostas)

    assert captured["story"] is story
    assert captured["respostas"] == respostas
    assert resultado.description == "descricao refinada"
    assert resultado.status == StoryStatus.DRAFT_VALIDATED
