import ssl
import socket
from urllib.parse import urlparse

def scan_tls(url):
    host = urlparse(url).hostname
    ctx = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=3) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
            return {
                "issuer": cert.get("issuer"),
                "subject": cert.get("subject"),
                "notAfter": cert.get("notAfter")
            }
