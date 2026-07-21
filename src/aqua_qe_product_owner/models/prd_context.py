from dataclasses import dataclass, field


@dataclass
class PRDContext:
    """Conteúdo do PRD além dos requisitos funcionais, conforme docs/standards/prd_standard.md."""

    vision: str = ""
    problem: str = ""
    objectives: list[str] = field(default_factory=list)
    target_audience: str = ""
    non_functional_requirements: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
