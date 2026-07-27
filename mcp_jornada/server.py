from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appUhF54ryb1rssOP")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN", "")
JOURNEYS_TABLE = os.getenv("AIRTABLE_JOURNEYS_TABLE", "Jornadas_Aluno")
EVENTS_TABLE = os.getenv("AIRTABLE_EVENTS_TABLE", "Eventos_Jornada")
AIRTABLE_API = "https://api.airtable.com/v0"

mcp = FastMCP(
    "Linha de Continuidade da Jornada do Aluno",
    instructions=(
        "Registre fatos da jornada sem inventar evolução, sem julgar o aluno e "
        "sempre separe fato observado, significado e próximo movimento."
    ),
    stateless_http=True,
    json_response=True,
)


def _headers() -> dict[str, str]:
    if not AIRTABLE_TOKEN:
        raise RuntimeError("AIRTABLE_TOKEN não configurado")
    return {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }


async def _create_record(table: str, fields: dict[str, Any]) -> dict[str, Any]:
    url = f"{AIRTABLE_API}/{AIRTABLE_BASE_ID}/{table}"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=_headers(), json={"fields": fields})
        response.raise_for_status()
        return response.json()


async def _list_records(table: str, formula: str) -> list[dict[str, Any]]:
    url = f"{AIRTABLE_API}/{AIRTABLE_BASE_ID}/{table}"
    params = {"filterByFormula": formula, "sort[0][field]": "Data_Evento", "sort[0][direction]": "asc"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=_headers(), params=params)
        response.raise_for_status()
        return response.json().get("records", [])


@mcp.tool()
def health() -> dict[str, Any]:
    """Confirma que o MCP está ativo e mostra a configuração não secreta."""
    return {
        "status": "alive",
        "base_id": AIRTABLE_BASE_ID,
        "journeys_table": JOURNEYS_TABLE,
        "events_table": EVENTS_TABLE,
        "token_configured": bool(AIRTABLE_TOKEN),
    }


@mcp.tool()
async def criar_jornada(
    jornada_id: str,
    pessoa_id: str,
    objetivo_declarado: str,
    ritmo_esperado_semanal: int = 2,
) -> dict[str, Any]:
    """Cria a linha de continuidade inicial de um aluno."""
    return await _create_record(
        JOURNEYS_TABLE,
        {
            "Jornada_ID": jornada_id,
            "Pessoa_ID": pessoa_id,
            "Objetivo_Declarado": objetivo_declarado,
            "Fase_Atual": "Entrada",
            "Estado_Jornada": "Ativa",
            "Data_Inicio": datetime.now(timezone.utc).date().isoformat(),
            "Ritmo_Esperado_Semanal": ritmo_esperado_semanal,
            "Ritmo_Atual_Semanal": 0,
            "Resumo_Continuidade": "Jornada iniciada. Aguardando os primeiros eventos confirmados.",
            "Proximo_Movimento": "Registrar a primeira prática ou presença.",
            "Precisa_Atencao": False,
        },
    )


@mcp.tool()
async def registrar_evento(
    evento_id: str,
    pessoa_id: str,
    tipo_evento: str,
    fato_observado: str,
    significado_para_jornada: str = "",
    origem: str = "Sistema",
    evidencia_referencia: str = "",
    visivel_para_aluno: bool = True,
    usar_em_narrativa: bool = True,
    confianca: str = "Confirmado",
) -> dict[str, Any]:
    """Registra um fato que passa a compor a história da jornada."""
    return await _create_record(
        EVENTS_TABLE,
        {
            "Evento_Jornada_ID": evento_id,
            "Pessoa_ID": pessoa_id,
            "Tipo_Evento": tipo_evento,
            "Data_Evento": datetime.now(timezone.utc).isoformat(),
            "Origem": origem,
            "Fato_Observado": fato_observado,
            "Significado_Para_Jornada": significado_para_jornada,
            "Evidencia_Referencia": evidencia_referencia,
            "Visivel_Para_Aluno": visivel_para_aluno,
            "Usar_Em_Narrativa": usar_em_narrativa,
            "Confianca": confianca,
        },
    )


@mcp.tool()
async def consultar_linha_do_tempo(pessoa_id: str) -> dict[str, Any]:
    """Retorna, em ordem cronológica, os eventos registrados para uma pessoa."""
    safe_id = pessoa_id.replace("'", "\\'")
    records = await _list_records(EVENTS_TABLE, f"{{Pessoa_ID}}='{safe_id}'")
    timeline = [
        {
            "id": record.get("id"),
            "tipo": record.get("fields", {}).get("Tipo_Evento"),
            "data": record.get("fields", {}).get("Data_Evento"),
            "fato": record.get("fields", {}).get("Fato_Observado"),
            "significado": record.get("fields", {}).get("Significado_Para_Jornada"),
            "confianca": record.get("fields", {}).get("Confianca"),
        }
        for record in records
    ]
    return {"pessoa_id": pessoa_id, "total_eventos": len(timeline), "linha_do_tempo": timeline}


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
