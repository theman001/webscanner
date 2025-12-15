def format_diff_markdown(summary):
    if not summary:
        return "### 🔄 Scan Diff Summary\n\n- No changes\n"
    lines = ["### 🔄 Scan Diff Summary\n"]
    lines += [f"- {s}" for s in summary]
    return "\n".join(lines) + "\n"
