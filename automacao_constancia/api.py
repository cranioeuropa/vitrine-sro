from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from runner import executar

app = FastAPI(title="NAVE CAP-ACA-002", version="0.4.0")
INTERNAL_KEY = os.getenv("NAVE_INTERNAL_KEY", "")


class CicloInput(BaseModel):
    acompanhamento_id: str
    reacao: str
    resposta_aluno: str = ""
    comportamento_7_dias: str
    treinos_7_dias: int = Field(ge=0, le=14)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "alive",
        "capacidade": "CAP-ACA-002",
        "versao": "0.4.0-auto",
        "airtable_configurado": bool(os.getenv("AIRTABLE_TOKEN")),
        "chave_interna_configurada": bool(INTERNAL_KEY),
    }


@app.post("/v1/capacidades/cap-aca-002/ciclo")
async def ciclo(
    payload: CicloInput,
    x_nave_key: str | None = Header(default=None),
) -> dict[str, Any]:
    if not INTERNAL_KEY:
        raise HTTPException(status_code=503, detail="NAVE_INTERNAL_KEY não configurada")
    if x_nave_key != INTERNAL_KEY:
        raise HTTPException(status_code=401, detail="Chave interna inválida")

    return await executar(
        acompanhamento_id=payload.acompanhamento_id,
        reacao=payload.reacao,
        resposta_aluno=payload.resposta_aluno,
        comportamento_7_dias=payload.comportamento_7_dias,
        treinos_7_dias=payload.treinos_7_dias,
    )
