import json
from pathlib import Path
from typing import Any

from libs.db.settings import get_settings

_DEFAULT_STATE: dict[str, Any] = {
    "workflows": {},
    "payment_intents": {},
    "payments": {},
    "audit_events": {},
    "ledger_syncs": {},
}


def _store_path() -> Path:
    settings = get_settings()
    path = Path(settings.runtime_store_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_state() -> dict[str, Any]:
    path = _store_path()
    if not path.exists():
        return dict(_DEFAULT_STATE)
    data = json.loads(path.read_text())
    state = dict(_DEFAULT_STATE)
    state.update(data)
    return state


def save_state(state: dict[str, Any]) -> None:
    path = _store_path()
    path.write_text(json.dumps(state, indent=2, sort_keys=True))


def reset_state() -> None:
    save_state(dict(_DEFAULT_STATE))

