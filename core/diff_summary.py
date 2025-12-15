def summarize_diff(diff):
    out = []
    for k,v in diff.items():
        if k == "dictionary_item_added":
            out += [f"➕ Added: {i}" for i in v]
        elif k == "dictionary_item_removed":
            out += [f"➖ Removed: {i}" for i in v]
        elif k == "values_changed":
            for p,c in v.items():
                out.append(f"🔄 Changed: {p}")
    return out
