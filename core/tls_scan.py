import ssl
import socket
from urllib.parse import urlparse

def scan_tls(url):
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 443

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=3) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                return {
                    "enabled": True,
                    "issuer": cert.get("issuer"),
                    "subject": cert.get("subject"),
                    "notAfter": cert.get("notAfter")
                }

    except (TimeoutError, socket.timeout):
        return {
            "enabled": False,
            "error": f"TLS connection timed out ({port} not reachable)"
        }

    except ConnectionRefusedError:
        return {
            "enabled": False,
            "error": f"TLS connection refused ({port} closed)"
        }

    except ssl.SSLError as e:
        return {
            "enabled": False,
            "error": f"TLS handshake failed: {e}"
        }

    except Exception as e:
        return {
            "enabled": False,
            "error": f"TLS scan error: {e}"
        }
