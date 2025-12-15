def summarize_tech_stack(http, result):
    stack = []
    headers = http.get("headers", {})

    if "server" in result.get("version", {}):
        stack.append("server")

    if "cloudflare" in headers.get("Server","").lower():
        stack.append("cdn")

    return stack
