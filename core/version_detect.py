import re

def detect_version(http, frameworks):
    headers = http.get("headers", {})
    versions = {}

    server = headers.get("Server")
    if server:
        versions["server"] = server
        m = re.search(r"/([\d.]+)", server)
        if m:
            versions["server_version"] = m.group(1)

    return versions
