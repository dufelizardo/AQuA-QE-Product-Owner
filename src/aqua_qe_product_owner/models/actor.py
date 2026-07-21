from dataclasses import dataclass


@dataclass
class Actor:
    """Ator (persona) identificado na fonte de entrada, com rastreabilidade (GR-1)."""

    name: str
    source_reference: str
