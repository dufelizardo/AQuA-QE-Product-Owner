def read_text_file(caminho: str) -> str:
    """Lê um arquivo de texto (.txt ou .md) e retorna seu conteúdo."""
    with open(caminho, encoding="utf-8") as arquivo:
        return arquivo.read()
