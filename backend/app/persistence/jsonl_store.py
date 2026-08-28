"""File-based JSONL persistence for NER-LDI prototype. No database required."""
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

RUNTIME_DIR = Path(__file__).parent.parent.parent.parent / "data" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()


def _get_path(store_name: str) -> Path:
    return RUNTIME_DIR / f"{store_name}.jsonl"


def append_event(store_name: str, event: dict) -> dict:
    """Append an event to a JSONL file. Returns the event with added metadata."""
    event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    event.setdefault("id", f"{store_name}_{int(datetime.now(timezone.utc).timestamp() * 1000)}")
    path = _get_path(store_name)
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")
    return event


def read_events(store_name: str, limit: int = 100, filter_fn=None) -> List[dict]:
    """Read events from a JSONL file, newest first."""
    path = _get_path(store_name)
    if not path.exists():
        return []
    events = []
    with _lock:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    if filter_fn:
        events = [e for e in events if filter_fn(e)]
    events.reverse()
    return events[:limit]


def find_event(store_name: str, event_id: str) -> Optional[dict]:
    """Find a specific event by ID."""
    events = read_events(store_name, limit=10000)
    for e in events:
        if e.get("id") == event_id:
            return e
    return None


def count_events(store_name: str) -> int:
    """Count total events in a store."""
    path = _get_path(store_name)
    if not path.exists():
        return 0
    with _lock:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
