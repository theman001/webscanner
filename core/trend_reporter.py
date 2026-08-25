def generate_trend_markdown(trend):
    if "risk_assessment" not in trend:
        note = trend.get("note", "insufficient history")
        return f"# 📈 Long-Term Scan Trend Report\n\n{note} (need at least 2 saved scans).\n"

    r = trend["risk_assessment"]
    s = trend["summary"]

    return f"""# 📈 Long-Term Scan Trend Report

## Summary
- Total scans: {s['total_scans']}
- First scan: {s['first_seen']}
- Last scan: {s['last_seen']}

## Stability & Risk
- Stability score: **{r['stability_score']}**
- Risk level: {r['indicator']} **{r['risk_level']}**
"""
