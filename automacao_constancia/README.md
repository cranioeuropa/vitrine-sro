# CAP-ACA-002 — Automação de Constância

Este pacote transforma o motor simulado de acompanhamento em uma circulação executável:

`evento → validação → CAP-ACA-002 → Airtable → recibo`

## Variáveis

```env
AIRTABLE_BASE_ID=app41ZgFVPphov2ot
AIRTABLE_TOKEN=pat_...
NAVE_INTERNAL_KEY=gere-uma-chave-local
NAVE_CAP_ACA_002_URL=http://host.docker.internal:8787/v1/capacidades/cap-aca-002/ciclo
```

## Instalação local

```powershell
cd automacao_constancia
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8787
```

Teste de saúde:

```powershell
Invoke-RestMethod http://localhost:8787/health
```

Teste do ciclo:

```powershell
$headers = @{ "X-NAVE-KEY" = $env:NAVE_INTERNAL_KEY }
$body = @{
  acompanhamento_id = "ACO-2026-002"
  reacao = "Responde positivamente"
  resposta_aluno = "A semana apertou, mas reorganizei meus horários."
  comportamento_7_dias = "Melhorou"
  treinos_7_dias = 4
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8787/v1/capacidades/cap-aca-002/ciclo `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

## n8n

Importe `n8n/CAP-ACA-002-workflow.json`.

Configure no ambiente do n8n:

- `NAVE_CAP_ACA_002_URL`
- `NAVE_INTERNAL_KEY`

Ative o workflow somente depois que `/health` responder e o teste manual criar os três recibos:

1. reação;
2. sequência;
3. execução simulada.

## Regra central

A resposta verbal do aluno não prova recuperação. O comportamento posterior é a evidência principal.
