import json, os
from datetime import datetime

HISTORY_DIR = "history"

def load_history():
    scans = []
    for f in sorted(os.listdir(HISTORY_DIR)):
        if f.endswith(".json"):
            scans.append(json.load(open(os.path.join(HISTORY_DIR,f))))
    return scans

def stability_risk(score):
    if score >= 0.85: return ("LOW","🟢")
    if score >= 0.70: return ("MEDIUM","🟡")
    if score >= 0.50: return ("HIGH","🟠")
    return ("CRITICAL","🔴")

def analyze_trends():
    scans = load_history()
    if len(scans) < 2:
        return {"note":"insufficient history"}

    changes = sum(1 for s in scans if s.get("diff",{}).get("enabled"))
    score = round(1 - changes/len(scans),2)
    level, emoji = stability_risk(score)

    return {
        "summary": {
            "total_scans": len(scans),
            "first_seen": scans[0]["metadata"]["timestamp"],
            "last_seen": scans[-1]["metadata"]["timestamp"]
        },
        "risk_assessment": {
            "stability_score": score,
            "risk_level": level,
            "indicator": emoji
        }
    }

def extract_timeseries(scans):
    dates, ports, subs = [], [], []
    for s in scans:
        dates.append(s["metadata"]["timestamp"].split("T")[0])
        r = s["result"]
        ports.append(len(r.get("ports",[])))
        subs.append(len(r.get("subdomains",[])))
    return dates, ports, subs
