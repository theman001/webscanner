import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fingerprint import detect_framework


def test_header_value_must_match_not_just_key():
    http = {"headers": {"Server": "AmazonS3"}, "body": ""}
    names = {f["name"] for f in detect_framework(http)}
    assert "nginx" not in names and "apache" not in names, names


def test_matching_header_value_still_detected():
    http = {"headers": {"Server": "nginx/1.18.0"}, "body": ""}
    names = {f["name"] for f in detect_framework(http)}
    assert "nginx" in names
    assert "apache" not in names


def test_presence_only_header_rule_still_works():
    http = {"headers": {"CF-RAY": "abc123"}, "body": ""}
    names = {f["name"] for f in detect_framework(http)}
    assert "cloudflare" in names


if __name__ == "__main__":
    test_header_value_must_match_not_just_key()
    test_matching_header_value_still_detected()
    test_presence_only_header_rule_still_works()
    print("ok")
