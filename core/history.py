import json, os
from deepdiff import DeepDiff
from datetime import datetime
from core.utils import resource_path

HISTORY_DIR = resource_path("history")

def list_history_files():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    return sorted(f for f in os.listdir(HISTORY_DIR) if f.endswith(".json"))

def save_snapshot(data):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # microseconds: avoid same-second filename collisions
    with open(os.path.join(HISTORY_DIR, f"scan_{ts}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def diff_last_scan(current):
    """Diff against the most recent EXISTING snapshot. Call this before
    save_snapshot() in the same run, so the current scan isn't diffed
    against itself."""
    files = list_history_files()
    if not files:
        return None
    with open(os.path.join(HISTORY_DIR, files[-1])) as f:
        prev = json.load(f)
    return DeepDiff(prev, current, ignore_order=True)
