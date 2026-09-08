"""Synthetic child-process recovery worker; it reads only durable JSON input."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from school_os.brief import recover_delivery
from school_os.catalog import recover_catalog_index
from school_os.tasks import reconcile_provider_tasks, recover_task_comment
from tests.support.fakes import FixtureTasks, SendSink


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _catalog(payload: dict) -> dict:
    result = recover_catalog_index(
        payload["source_bodies"], base64.b64decode(payload["intended_b64"]),
        base64.b64decode(payload["persisted_b64"]), payload["index"], payload["facts"],
    )
    return {"record_id": result.record_id, "index": result.index}


def _task(payload: dict) -> dict:
    provider = FixtureTasks()
    provider.tasks = [dict(task) for task in payload["provider_tasks"]]
    result = reconcile_provider_tasks(
        provider, payload["register"], payload["provider_state"],
        task_schema=_schema("task.schema.json"),
        register_schema=_schema("canonical-tasks.schema.json"),
        provider_state_schema=_schema("provider-state.schema.json"),
    )
    return {
        "provider_task_count": len(provider.tasks),
        "bindings": result.provider_state["bindings"],
        "effects": list(result.effects),
    }


def _comment(payload: dict) -> dict:
    provider = FixtureTasks()
    provider.comments = [dict(comment) for comment in payload["comments"]]
    comment = recover_task_comment(provider, payload["provider_object_id"], payload["effect_id"], payload["text"])
    return {"comment": comment, "comment_count": len(provider.comments)}


def _delivery(payload: dict) -> dict:
    content = base64.b64decode(payload["content_b64"])
    sink = SendSink()
    sink.deliveries = [content]
    ledger = recover_delivery(
        sink, payload["ledger"], delivery_key=payload["delivery_key"], content=content,
        ledger_schema=_schema("delivery-ledger.schema.json"),
    )
    return {"ledger": ledger, "delivery_count": len(sink.deliveries)}


def main(input_path: Path, output_path: Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    handlers = {"catalog": _catalog, "task": _task, "comment": _comment, "delivery": _delivery}
    output_path.write_text(json.dumps(handlers[payload["kind"]](payload), sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
