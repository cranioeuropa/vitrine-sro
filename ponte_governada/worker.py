from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

BASE_ID = os.getenv("AIRTABLE_BASE_ID", "app41ZgFVPphov2ot")
TOKEN = os.getenv("AIRTABLE_TOKEN", "")
TABLE = os.getenv("NAVE_QUEUE_TABLE", "FILA_DE_MOVIMENTOS")
POLL_SECONDS = int(os.getenv("NAVE_POLL_SECONDS", "20"))
REPO = Path(os.getenv("NAVE_REPO_PATH", r"C:\Users\Cranio\Projetos\vitrine-sro")).resolve()
POLICY_PATH = Path(__file__).with_name("policy.json")
API = "https://api.airtable.com/v0"

STATUS_READY = "Pronto para executar"
STATUS_RUNNING = "Em execução"
STATUS_DONE = "Concluído"
STATUS_BLOCKED = "Bloqueado"


def headers() -> dict[str, str]:
    if not TOKEN:
        raise RuntimeError("AIRTABLE_TOKEN não configurado")
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    with httpx.Client(timeout=45) as client:
        response = client.request(method, f"{API}/{BASE_ID}/{path}", headers=headers(), **kwargs)
        response.raise_for_status()
        return response.json()


def fetch_ready() -> list[dict[str, Any]]:
    formula = "AND({STATUS}='Pronto para executar',{CONECTOR_NECESSARIO}='PC Crânio')"
    data = request("GET", TABLE, params={"filterByFormula": formula, "maxRecords": 3})
    return data.get("records", [])


def patch(record_id: str, fields: dict[str, Any]) -> None:
    request("PATCH", TABLE, json={"records": [{"id": record_id, "fields": fields}]})


def parse_payload(fields: dict[str, Any]) -> dict[str, Any]:
    raw = fields.get("OBSERVACOES", "")
    marker = "PONTE_JSON:"
    if marker not in raw:
        raise ValueError("OBSERVACOES não contém PONTE_JSON")
    return json.loads(raw.split(marker, 1)[1].strip())


def run_operation(operation: str, policy: dict[str, Any]) -> dict[str, Any]:
    definition = policy.get("operations", {}).get(operation)
    if not definition or not definition.get("enabled", False):
        raise PermissionError(f"Operação não autorizada: {operation}")

    command = definition["command"]
    cwd = (REPO / definition.get("cwd", ".")).resolve()
    if REPO not in cwd.parents and cwd != REPO:
        raise PermissionError("Diretório fora do repositório governado")

    completed = subprocess.run(
        command,
        cwd=cwd,
        shell=False,
        capture_output=True,
        text=True,
        timeout=int(definition.get("timeout_seconds", 120)),
        check=False,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()[-12000:]
    return {"exit_code": completed.returncode, "output": output, "ok": completed.returncode == 0}


def process(record: dict[str, Any], policy: dict[str, Any]) -> None:
    record_id = record["id"]
    fields = record.get("fields", {})
    movement_id = fields.get("ID_MOVIMENTO", record_id)
    patch(record_id, {"STATUS": STATUS_RUNNING, "OBSERVACOES": fields.get("OBSERVACOES", "") + f"\nINICIO_PONTE: {now()}"})

    try:
        payload = parse_payload(fields)
        operation = payload["operation"]
        result = run_operation(operation, policy)
        final_status = STATUS_DONE if result["ok"] else STATUS_BLOCKED
        receipt = {
            "movement_id": movement_id,
            "operation": operation,
            "finished_at": now(),
            **result,
        }
        patch(record_id, {
            "STATUS": final_status,
            "OBSERVACOES": fields.get("OBSERVACOES", "") + "\nRECIBO_PONTE:" + json.dumps(receipt, ensure_ascii=False),
            "PROXIMO_PASSO_HUMANO": "Nenhum" if result["ok"] else "Revisar o recibo e corrigir a falha antes de repetir.",
        })
    except Exception as exc:
        patch(record_id, {
            "STATUS": STATUS_BLOCKED,
            "OBSERVACOES": fields.get("OBSERVACOES", "") + f"\nERRO_PONTE: {type(exc).__name__}: {exc}",
            "PROXIMO_PASSO_HUMANO": "Revisar política, payload ou credenciais.",
        })


def main() -> None:
    policy = load_policy()
    print(f"Ponte Governada ativa | fila={TABLE} | intervalo={POLL_SECONDS}s | repo={REPO}")
    while True:
        try:
            for record in fetch_ready():
                process(record, policy)
        except Exception as exc:
            print(f"Falha de ronda: {type(exc).__name__}: {exc}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
