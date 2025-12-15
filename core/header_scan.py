SEC_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy"
]

def analyze_security_headers(http):
    headers = http.get("headers", {})
    return {
        h: headers.get(h)
        for h in SEC_HEADERS
        if h in headers
    }
