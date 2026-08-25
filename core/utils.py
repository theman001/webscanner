import logging
import os
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resource_path(*parts):
    return os.path.join(BASE_DIR, *parts)

def validate_url(url):
    p = urlparse(url)
    if p.scheme not in ("http","https"):
        raise ValueError("Invalid URL")

def init_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger("webscanner")

def parse_choices(raw, valid_choices, full_value):
    if raw.strip().upper() == "FULL":
        return {"FULL"}
    items = set()
    for x in raw.split(","):
        x = x.strip()
        if not x.isdigit() or x not in valid_choices:
            raise ValueError(f"Invalid choice: {x}")
        items.add(x)
    if full_value in items:
        return {"FULL"}
    return items

def safe_select(prompt, valid_choices, full_value):
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("No input")
            continue
        try:
            return parse_choices(raw, valid_choices, full_value)
        except ValueError as e:
            print(e)

def configure_performance(interactive=False):
    defaults = {
        "dns_timeout": 1.0,
        "port_timeout": 1.0,
        "http_timeout": 5.0,
        "concurrency": 50
    }
    if not interactive:
        return defaults

    perf = {}
    for key, default in defaults.items():
        raw = input(f"{key} [{default}]: ").strip()
        if not raw:
            perf[key] = default
            continue
        try:
            perf[key] = type(default)(raw)
        except ValueError:
            print(f"Invalid value, using default {default}")
            perf[key] = default
    return perf
