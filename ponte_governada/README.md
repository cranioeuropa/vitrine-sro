# Ponte Remota Governada

A ponte transforma a fila existente do Airtable em uma porta de execução controlada no PC Crânio.

## Fluxo

`ChatGPT/Airtable → FILA_DE_MOVIMENTOS → trabalhador local → operação autorizada → recibo na própria fila`

## Segurança

- não aceita comandos de texto livre;
- não usa `shell=True`;
- executa somente operações presentes em `policy.json`;
- limita o diretório ao repositório governado;
- registra início, resultado, saída e erro;
- operações destrutivas, publicação, exclusão, gasto e credenciais não fazem parte da política.

## Payload da fila

Crie um movimento com:

- `STATUS`: `Pronto para executar`
- `CONECTOR_NECESSARIO`: `PC Crânio`
- `OBSERVACOES` contendo:

```text
PONTE_JSON:{"operation":"health_repo"}
```

Operações iniciais:

```text
health_repo
git_status
git_pull_current_branch
test_cap_aca_002
health_cap_aca_002
```

## Primeira ativação no Windows

```powershell
cd C:\Users\Cranio\Projetos\vitrine-sro
git pull
cd ponte_governada
$env:AIRTABLE_TOKEN = "TOKEN_LOCAL_EXISTENTE"
.\iniciar.ps1
```

O token permanece apenas no ambiente local. Nunca deve entrar no GitHub, no Airtable ou na conversa.

## Estado operacional

A ponte só passa a operar remotamente depois que `iniciar.ps1` estiver rodando no PC. A partir daí, novas operações autorizadas podem ser colocadas na fila sem presença diante do computador.
