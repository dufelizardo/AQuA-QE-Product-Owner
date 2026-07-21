from dataclasses import dataclass


@dataclass
class Requirement:
    """Requisito candidato extraído da fonte de entrada por extract_requirements."""

    id: str
    text: str
    source_reference: str
