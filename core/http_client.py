import requests

def fetch_http_info(url, perf=None):
    timeout = perf["http_timeout"] if perf else 5.0
    r = requests.get(url, timeout=timeout, verify=False)

    return {
        "status": r.status_code,
        "headers": dict(r.headers),
        "body": r.text[:5000]
    }
