import json
import re
import os

FP_PATH = os.path.join("data", "fingerprints.json")

with open(FP_PATH, "r", encoding="utf-8") as f:
    FINGERPRINTS = json.load(f)

def detect_framework(http):
    headers = http.get("headers", {})
    body = http.get("body", "")
    found = []

    for name, rules in FINGERPRINTS.items():
        score = 0
        evidence = []

        for h in rules.get("headers", []):
            if h in headers:
                score += 1
                evidence.append(f"header:{h}")

        for p in rules.get("body_patterns", []):
            if re.search(p, body, re.I):
                score += 1
                evidence.append(f"body:{p}")

        if score:
            found.append({
                "name": name,
                "score": score,
                "evidence": evidence
            })

    return found
