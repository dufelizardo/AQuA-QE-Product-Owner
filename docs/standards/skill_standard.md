# Padrão de Skill

> Estrutura padrão para as Skills (funções que o agente pode executar) desta plataforma. Define o formato; a lista de skills deste agente fica em `../agent/skills.md` e a implementação em `../../src/aqua_qe_product_owner/skills/`.

## Propósito

Uma Skill é uma unidade de capacidade do agente: uma função com contrato claro de entrada/saída, que o agente invoca para realizar uma etapa concreta do seu trabalho (ex.: ler um arquivo de texto, identificar um ator, gerar uma história).

## Campos por skill

- **Nome**: `<nome da função, em snake_case>`
- **Descrição**: `<o que a skill faz, em uma frase>`
- **Entrada**: `<parâmetros e tipos>`
- **Saída**: `<tipo de retorno e formato>`
- **Efeitos colaterais**: `<leitura/escrita de arquivo, chamada de API externa, nenhum>`
- **Erros esperados**: `<condições em que a skill deve falhar explicitamente em vez de retornar um resultado inválido>`
- **Dependências**: `<outras skills ou recursos externos necessários>`

## Convenções de implementação

- Cada skill vive em seu próprio arquivo, com uma função pública por arquivo (ver `src/aqua_qe_product_owner/skills/`).
- Assinatura com type hints completos; docstring curta (uma linha) descrevendo o propósito.
- Skills são **determinísticas em contrato**: dado o mesmo input, o formato da saída não muda, mesmo que o conteúdo varie.
- Skills não devem conter lógica de orquestração (decidir qual skill chamar em seguida) — isso é responsabilidade do agente/orquestrador (ver `system_design_standard.md`).

## Critérios de qualidade

- Skill deve ser testável isoladamente, sem precisar do agente completo em execução.
- Skill deve fazer uma única coisa (equivalente ao critério "Singular" de um requisito bem escrito, ver `../../knowledge/methodology/iso29148.md`).
- Nome da skill deve deixar claro o que ela faz sem precisar ler a implementação.
