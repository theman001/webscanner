import requests

def fetch_http_info(url, perf=None):
    timeout = perf.get("http_timeout", 5.0) if perf else 5.0

    try:
        r = requests.get(
            url,
            timeout=timeout,
            verify=False,
            allow_redirects=True
        )
        return {
            "enabled": True,
            "status": r.status_code,
            "headers": dict(r.headers),
            "body": r.text[:5000]
        }

    except requests.exceptions.Timeout:
        return {"enabled": False, "error": "HTTP timeout"}

    except requests.exceptions.SSLError as e:
        return {"enabled": False, "error": f"SSL error: {e}"}

    except requests.exceptions.RequestException as e:
        return {"enabled": False, "error": f"HTTP error: {e}"}
