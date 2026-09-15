import json
from datetime import datetime, timezone
from pathlib import Path

from config import settings

HISTORY_FILE = Path(settings.BASE_DIR) / "research_history.json"


def _ensure_history_file() -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def list_history() -> list[dict]:
    _ensure_history_file()
    with HISTORY_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_history_item(question: str, report: dict, sources: list[dict]) -> dict:
    _ensure_history_file()
    history = list_history()
    item = {
        "id": f"research-{datetime.now(timezone.utc).timestamp()}",
        "question": question,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report": report,
        "sources": sources,
    }
    history.insert(0, item)
    with HISTORY_FILE.open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)
    return item


def delete_history_item(item_id: str) -> bool:
    _ensure_history_file()
    history = list_history()
    filtered = [item for item in history if item.get("id") != item_id]
    with HISTORY_FILE.open("w", encoding="utf-8") as handle:
        json.dump(filtered, handle, indent=2)
    return len(filtered) != len(history)
