from aqua_qe_product_owner.models import AcceptanceCriteria, StoryStatus, UserStory
from aqua_qe_product_owner.workflow import generate_acceptance as workflow_module


def test_generate_acceptance_appends_new_criteria_and_finalizes(monkeypatch):
    story = UserStory(
        id="US-001",
        title="titulo",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="c1", given="g1", when="w1", then="t1")
        ],
        source_reference="fonte",
    )

    monkeypatch.setattr(
        workflow_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "criterios_aceitacao": [{"cenario": "c2", "dado": "g2", "quando": "w2", "entao": "t2"}]
        },
    )

    def fake_finalize_story(story):
        story.status = StoryStatus.DRAFT_VALIDATED
        return story

    monkeypatch.setattr(workflow_module, "finalize_story", fake_finalize_story)

    resultado = workflow_module.generate_acceptance(story)

    assert len(resultado.acceptance_criteria) == 2
    assert resultado.acceptance_criteria[0].id == "AC-001"
    assert resultado.acceptance_criteria[1] == AcceptanceCriteria(
        id="AC-002", scenario="c2", given="g2", when="w2", then="t2"
    )
    assert resultado.status == StoryStatus.DRAFT_VALIDATED
