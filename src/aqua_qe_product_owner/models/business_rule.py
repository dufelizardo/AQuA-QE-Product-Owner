from dataclasses import dataclass


@dataclass
class BusinessRule:
    """Regra de negócio identificada na fonte, conforme knowledge/templates/business_rule.md."""

    id: str
    description: str
    source_reference: str
