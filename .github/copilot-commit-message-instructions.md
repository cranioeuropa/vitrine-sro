# Instruções para mensagens de commit

Gere mensagens compatíveis com Conventional Commits.

## Formato obrigatório

```text
tipo(escopo): descrição
```

Quando houver informação relevante adicional, use um corpo curto após uma linha em branco.

## Tipos permitidos

- `feat`: nova capacidade ou comportamento;
- `fix`: correção de falha;
- `refactor`: reorganização sem mudança funcional intencional;
- `test`: criação ou melhoria de testes;
- `docs`: documentação;
- `chore`: manutenção, dependências ou configuração;
- `ci`: integração, entrega, deploy ou automação de pipeline;
- `perf`: melhoria de desempenho;
- `security`: melhoria de segurança.

## Regras de escrita

- Escreva a mensagem em inglês.
- Use letras minúsculas no tipo e no escopo.
- Use verbo no imperativo na descrição.
- Descreva o resultado concreto da alteração.
- Use um escopo curto que represente módulo, órgão, serviço ou capacidade.
- Mantenha a primeira linha preferencialmente com até 72 caracteres.
- Não termine a primeira linha com ponto.
- Não use mensagens vagas como `update files`, `changes`, `adjustments`, `misc` ou `fix stuff`.
- Não inclua nomes de ferramentas como Copilot na mensagem, salvo quando a própria ferramenta for o objeto da mudança.
- Quando existirem alterações de naturezas diferentes, priorize a mudança principal e mencione as secundárias no corpo.

## Escopos iniciais sugeridos

- `governance`
- `repository`
- `workflow`
- `operator`
- `evidence`
- `catalog`
- `api`
- `ui`
- `database`
- `deploy`
- `docs`

## Exemplos bons

```text
feat(evidence): persist workflow execution result
fix(api): reject missions without an identifier
refactor(operator): separate validation from execution
test(workflow): cover failed execution recovery
docs(governance): document commit convention
ci(deploy): validate build before release
security(api): prevent secrets from reaching logs
```

## Exemplos ruins

```text
update files
changes
fixed bug
final version
now it works
```

Antes de sugerir a mensagem, analise somente as alterações preparadas para commit e não invente resultados que não estejam demonstrados no diff.
