from __future__ import annotations

import argparse
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

BASE_ID = os.getenv("AIRTABLE_BASE_ID", "app41ZgFVPphov2ot")
TOKEN = os.getenv("AIRTABLE_TOKEN", "")
API = "https://api.airtable.com/v0"

TABLE_ACOMPANHAMENTO = "ALUNOS_EM_ACOMPANHAMENTO"
TABLE_REACOES = "SIMULADOR_DE_REACOES"
TABLE_SEQUENCIAS = "SEQUENCIAS_DE_ACOMPANHAMENTO"
TABLE_EXECUCOES = "EXECUCOES_SIMULADAS"


@dataclass(frozen=True)
class Decisao:
    estado_final: str
    acao_final: str
    resultado: str
    leitura: str
    exige_humano: bool = False
    interrompe_automacao: bool = False


def headers() -> dict[str, str]:
    if not TOKEN:
        raise RuntimeError("AIRTABLE_TOKEN não configurado")
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


async def buscar_por_campo(table: str, field: str, value: str) -> dict[str, Any]:
    safe = value.replace("'", "\\'")
    params = {"filterByFormula": f"{{{field}}}='{safe}'", "maxRecords": 1}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{API}/{BASE_ID}/{table}", headers=headers(), params=params)
        response.raise_for_status()
        records = response.json().get("records", [])
    if not records:
        raise ValueError(f"Registro não encontrado em {table}: {field}={value}")
    return records[0]


async def criar(table: str, fields: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{API}/{BASE_ID}/{table}", headers=headers(), json={"fields": fields}
        )
        response.raise_for_status()
        return response.json()


def decidir(reacao: str, treinos_7_dias: int, comportamento: str) -> Decisao:
    if reacao == "Pede silêncio":
        return Decisao(
            "Silenciado", "Silenciar contato", "Prejudicial",
            "Preferência explícita encerra contatos automáticos.",
            interrompe_automacao=True,
        )
    if reacao in {"Sente cobrança", "Revela dificuldade"}:
        return Decisao(
            "Humano", "Encaminhar humano", "Eficaz" if reacao == "Revela dificuldade" else "Prejudicial",
            "Sinal humano relevante exige interrupção da automação e revisão assistida.",
            exige_humano=True, interrompe_automacao=True,
        )
    if treinos_7_dias >= 3 or comportamento == "Melhorou":
        return Decisao(
            "Saudável", "Manter acompanhamento", "Eficaz",
            "A melhora comportamental confirma recuperação do ritmo; a fala isolada não seria suficiente.",
        )
    if treinos_7_dias == 1:
        return Decisao(
            "Atenção leve", "Aguardar", "Eficaz",
            "O retorno começou, mas ainda não há consistência suficiente para declarar recuperação.",
        )
    return Decisao(
        "Queda", "Pergunta leve", "Ineficaz",
        "Sem mudança comportamental após uma intervenção; manter observação proporcional.",
    )


async def executar(
    acompanhamento_id: str,
    reacao: str,
    resposta_aluno: str,
    comportamento_7_dias: str,
    treinos_7_dias: int,
) -> dict[str, Any]:
    aluno = await buscar_por_campo(TABLE_ACOMPANHAMENTO, "ID_ACOMPANHAMENTO", acompanhamento_id)
    dados = aluno["fields"]
    decisao = decidir(reacao, treinos_7_dias, comportamento_7_dias)
    sufixo = uuid.uuid4().hex[:8].upper()
    agora = datetime.now(timezone.utc).isoformat()
    reacao_id = f"REA-AUTO-{sufixo}"
    seq_id = f"SEQ-AUTO-{sufixo}"
    exe_id = f"EXE-AUTO-{sufixo}"

    await criar(TABLE_REACOES, {
        "ID_REACAO": reacao_id,
        "ID_ACOMPANHAMENTO": acompanhamento_id,
        "TIPO_MENSAGEM": dados.get("TIPO_DE_ACAO", "Pergunta leve"),
        "MENSAGEM_ENVIADA": dados.get("MENSAGEM_SUGERIDA", ""),
        "REACAO_SIMULADA": reacao,
        "RESPOSTA_DO_ALUNO": resposta_aluno,
        "COMPORTAMENTO_7_DIAS": comportamento_7_dias,
        "TREINOS_7_DIAS": treinos_7_dias,
        "RESULTADO_INTERVENCAO": decisao.resultado,
        "PROXIMA_ACAO": decisao.acao_final,
        "APRENDIZADO_GERADO": decisao.leitura,
        "EXIGE_HUMANO": decisao.exige_humano,
        "DATA_SIMULACAO": agora,
    })

    await criar(TABLE_SEQUENCIAS, {
        "ID_SEQUENCIA": seq_id,
        "ESTADO_INICIAL": dados.get("TENDENCIA", "Atenção leve"),
        "EVENTOS_DA_SEQUENCIA": (
            f"Mensagem enviada → {reacao} → {comportamento_7_dias} "
            f"({treinos_7_dias} treinos em 7 dias)"
        ),
        "ESTADO_FINAL": decisao.estado_final,
        "ACAO_FINAL": decisao.acao_final,
        "INTERVENCOES": 1,
        "EXIGE_HUMANO": decisao.exige_humano,
        "INTERROMPE_AUTOMACAO": decisao.interrompe_automacao,
        "LEITURA_DO_MOTOR": decisao.leitura,
        "RESULTADO_TESTE": "Aprovado",
        "VERSAO_MOTOR": "0.4.0-auto",
    })

    await criar(TABLE_EXECUCOES, {
        "ID_EXECUCAO": exe_id,
        "ID_CAPACIDADE": "CAP-ACA-002",
        "VERSAO": "0.4.0-auto",
        "ID_CENARIO": f"{acompanhamento_id} / {reacao_id} / {seq_id}",
        "DECISAO_TOMADA": decisao.acao_final,
        "RESPOSTA_PRODUZIDA": decisao.leitura,
        "FERRAMENTA_PREVISTA": "Executor Python CAP-ACA-002; n8n como orquestrador.",
        "CUSTO_ESTIMADO": 0,
        "RISCO_DETECTADO": "Não aceitar fala isolada como prova; observar comportamento posterior.",
        "EXIGE_APROVACAO_HUMANA": decisao.exige_humano,
        "RESULTADO": "Aprovado",
        "EVIDENCIAS": f"{reacao_id}; {seq_id}",
        "DATA_EXECUCAO": agora,
    })

    return {
        "status": "concluido",
        "capacidade": "CAP-ACA-002",
        "acompanhamento_id": acompanhamento_id,
        "reacao_id": reacao_id,
        "sequencia_id": seq_id,
        "execucao_id": exe_id,
        "decisao": decisao.__dict__,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa um ciclo automático da CAP-ACA-002")
    parser.add_argument("--acompanhamento", required=True)
    parser.add_argument("--reacao", required=True)
    parser.add_argument("--resposta", default="")
    parser.add_argument("--comportamento", required=True)
    parser.add_argument("--treinos", type=int, required=True)
    args = parser.parse_args()

    import asyncio
    resultado = asyncio.run(executar(
        args.acompanhamento, args.reacao, args.resposta, args.comportamento, args.treinos
    ))
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
