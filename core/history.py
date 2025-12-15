import json, os
from deepdiff import DeepDiff
from datetime import datetime

HISTORY_DIR = "history"

def save_snapshot(data):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"{HISTORY_DIR}/scan_{ts}.json","w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

def diff_last_scan(current):
    files = sorted(os.listdir(HISTORY_DIR))
    if len(files) < 2:
        return None
    with open(os.path.join(HISTORY_DIR, files[-2])) as f:
        prev = json.load(f)
    return DeepDiff(prev, current, ignore_order=True)
