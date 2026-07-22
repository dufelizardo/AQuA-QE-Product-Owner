from ..models import PRDDraft
from ..services.confluence_service import update_page
from .format_prd_markdown import format_prd_markdown


def update_confluence_page(page_id: str, draft: PRDDraft) -> None:
    """Persiste a versão atual de um PRD aceito de volta numa página existente do Confluence Cloud."""
    update_page(page_id, format_prd_markdown(draft))
