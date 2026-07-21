from ..models import UserStory
from ..skills.refine_story import refine_story
from .generate_user_story import finalize_story


def refine_user_story(story: UserStory, respostas: list[dict]) -> UserStory:
    """Reescreve uma User Story com base nas respostas do usuário e reaplica validação/revisão."""
    story_refinada = refine_story(story, respostas)
    return finalize_story(story_refinada)
