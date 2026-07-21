# Template — Acceptance Criteria

> Estrutura padrão, sem conteúdo de domínio. Critérios de aceitação tornam uma User Story testável (ver `../methodology/invest.md`).

## Formato Given-When-Then (Gherkin)

```gherkin
Scenario: <nome do cenário>
  Given <contexto/estado inicial>
  When <ação ou evento>
  Then <resultado esperado>
  And <resultado adicional, se necessário>
```

Ver `../methodology/gherkin.md` para a sintaxe completa e `../methodology/bdd.md` para o raciocínio por trás do formato.

## Campos complementares

- **ID**: `<identificador único, ex.: AC-001>`
- **User Story relacionada**: `<referência à história — ver template user_story.md>`
- **Cenário(s)**: `<um ou mais blocos Given-When-Then, cobrindo caminho feliz e exceções relevantes>`
- **Tipo**: `<funcional | não funcional (desempenho, segurança, usabilidade etc.) — ver ../methodology/babok.md>`

## Checklist de qualidade

Cada critério deve ser, individualmente (ver `../methodology/iso29148.md`):

- Não ambíguo (uma única interpretação possível).
- Singular (testa uma única condição por cenário).
- Verificável (existe forma objetiva de confirmar que passou ou falhou).
- Escrito do ponto de vista do comportamento observável, não da implementação técnica.
