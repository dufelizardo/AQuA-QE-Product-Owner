import re

from ..services.confluence_service import get_page_text


def read_confluence_page(pagina: str) -> str:
    """Busca uma página do Confluence Cloud (aceita a URL completa ou apenas o ID) e retorna título + corpo como texto simples."""
    match = re.search(r"/pages/(\d+)", pagina)
    page_id = match.group(1) if match else pagina
    return get_page_text(page_id)
