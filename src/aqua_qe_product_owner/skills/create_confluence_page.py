import os

from ..models import PRDDraft
from ..services.confluence_service import create_page
from .format_prd_markdown import format_prd_markdown


def create_confluence_page(draft: PRDDraft, titulo: str) -> str:
    """Publica o PRD aceito como uma nova página no Confluence Cloud e retorna a URL da página criada."""
    space_key = os.environ["CONFLUENCE_SPACE_KEY"]
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")

    page_id = create_page(space_key, titulo, format_prd_markdown(draft))
    return f"{base_url}/wiki/pages/viewpage.action?pageId={page_id}"
