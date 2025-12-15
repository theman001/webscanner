import logging
from urllib.parse import urlparse

def validate_url(url):
    p = urlparse(url)
    if p.scheme not in ("http","https"):
        raise ValueError("Invalid URL")

def init_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger("webscanner")

def safe_select(prompt, valid_choices, full_value):
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("No input")
            continue
        items = set()
        for x in raw.split(","):
            x=x.strip()
            if not x.isdigit() or x not in valid_choices:
                print("Invalid choice:",x)
                break
            items.add(x)
        else:
            if full_value in items:
                return {"FULL"}
            return items

def configure_performance():
    return {
        "dns_timeout": 1.0,
        "port_timeout": 1.0,
        "http_timeout": 5.0,
        "concurrency": 50
    }
