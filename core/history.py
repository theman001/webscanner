import json, os
from deepdiff import DeepDiff
from datetime import datetime
from core.utils import resource_path, target_host

HISTORY_DIR = resource_path("history")

def history_dir_for(target):
    """history/<host> — one target's snapshots, isolated from every other target's."""
    path = os.path.join(HISTORY_DIR, target_host(target))
    os.makedirs(path, exist_ok=True)
    return path

def list_history_files(target):
    return sorted(f for f in os.listdir(history_dir_for(target)) if f.endswith(".json"))

def save_snapshot(target, data):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # microseconds: avoid same-second filename collisions
    with open(os.path.join(history_dir_for(target), f"scan_{ts}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def diff_last_scan(target, current):
    """Diff against target's most recent EXISTING snapshot. Call this before
    save_snapshot() in the same run, so the current scan isn't diffed
    against itself."""
    files = list_history_files(target)
    if not files:
        return None
    with open(os.path.join(history_dir_for(target), files[-1])) as f:
        prev = json.load(f)
    return DeepDiff(prev, current, ignore_order=True)
