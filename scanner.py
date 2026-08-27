import argparse
import json
import asyncio
import os
import sys
import time
from datetime import datetime

from core.utils import (
    validate_url,
    safe_select,
    parse_choices,
    configure_performance,
    init_logger,
    report_dir_for
)

from core.http_client import fetch_http_info
from core.fingerprint import detect_framework
from core.version_detect import detect_version
from core.dns_enum_async import enumerate_subdomains_async
from core.port_scan_async import scan_ports_async
from core.service_infer import infer_services
from core.header_scan import analyze_security_headers
from core.tls_scan import scan_tls
from core.tech_stack import summarize_tech_stack

from core.history import save_snapshot, diff_last_scan
from core.diff_summary import summarize_diff
from core.diff_formatter import format_diff_markdown

from core.stats import init_stats
from core.profiler import profile

from core.trend_analyzer import (
    analyze_trends,
    extract_timeseries,
    load_history
)
from core.trend_reporter import generate_trend_markdown
from core.trend_graph import plot_trend

from core.ai_explainer import explain_risk_natural_language


# =========================
# Input helpers
# =========================

def input_target_url():
    while True:
        url = input("\n[+] Enter target URL (http/https): ").strip()
        if not url:
            print("❌ URL cannot be empty")
            continue
        try:
            validate_url(url)
            return url
        except ValueError as e:
            print(f"❌ Invalid URL: {e}")


# =========================
# Menu selections
# =========================

OPTIONS_CHOICES = {"1", "2", "3", "4", "5", "6"}
OPTIONS_FULL = "6"

def select_options():
    print("""
[ OPTIONS ]
--------------------------------
1. Scan history diff
2. Save scan snapshot
3. Configure scan performance
4. Long-term trend analysis
5. AI risk explanation
6. FULL OPTIONS
--------------------------------
""")
    return safe_select(
        prompt="Select options: ",
        valid_choices=OPTIONS_CHOICES,
        full_value=OPTIONS_FULL
    )


SCANS_CHOICES = {"1", "2", "3", "4", "5", "6", "7", "8"}
SCANS_FULL = "8"

def select_scans():
    print("""
[ SCANS ]
--------------------------------
1. Web framework & version
2. Subdomain scan
3. Port scan
4. Port → service inference
5. TLS / certificate
6. Security headers
7. Technology stack summary
8. FULL SCAN
--------------------------------
""")
    return safe_select(
        prompt="Select scans: ",
        valid_choices=SCANS_CHOICES,
        full_value=SCANS_FULL
    )


# =========================
# CLI (non-interactive)
# =========================

def parse_args():
    parser = argparse.ArgumentParser(
        description="WebScanner - pre-recon web exposure scanner"
    )
    parser.add_argument(
        "url", nargs="?",
        help="Target URL (http/https). Omit for interactive mode."
    )
    parser.add_argument("--options", help="OPTIONS selection, e.g. '1,2,4' or 'FULL'")
    parser.add_argument("--scans", help="SCANS selection, e.g. '1,2,3' or 'FULL'")
    parser.add_argument("--dns-timeout", type=float)
    parser.add_argument("--port-timeout", type=float)
    parser.add_argument("--http-timeout", type=float)
    parser.add_argument("--concurrency", type=int)
    args = parser.parse_args()

    if args.url and not (args.options and args.scans):
        parser.error("--options and --scans are required when URL is given (non-interactive mode)")

    return args


# =========================
# Main
# =========================

def main():
    logger = init_logger()
    args = parse_args()

    # 1️⃣ URL / 옵션 / 스캔 선택
    if args.url:
        try:
            validate_url(args.url)
            options = parse_choices(args.options, OPTIONS_CHOICES, OPTIONS_FULL)
            scans = parse_choices(args.scans, SCANS_CHOICES, SCANS_FULL)
        except ValueError as e:
            print(f"❌ {e}")
            sys.exit(1)
        target = args.url
    else:
        target = input_target_url()
        options = select_options()
        scans = select_scans()

    logger.info(f"target={target} options={sorted(options)} scans={sorted(scans)}")
    report_dir = report_dir_for(target)

    # 2️⃣ 성능 설정 (옵션 3 선택 시 대화형 프롬프트, CLI 인자가 최종 오버라이드)
    want_perf_prompt = (not args.url) and ("FULL" in options or "3" in options)
    perf = configure_performance(interactive=want_perf_prompt)
    for key, val in (
        ("dns_timeout", args.dns_timeout),
        ("port_timeout", args.port_timeout),
        ("http_timeout", args.http_timeout),
        ("concurrency", args.concurrency),
    ):
        if val is not None:
            perf[key] = val

    # 4️⃣ 통계 / 타이밍
    stats = init_stats()
    timings = {}

    result = {}
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "options_selected": list(options),
        "scans_selected": list(scans),
        "performance": perf
    }

    total_start = time.perf_counter()

    http = None

    # =========================
    # SCANS
    # =========================

    if "FULL" in scans or "1" in scans:
        logger.info("scan: framework & version")
        with profile("framework_scan", timings):
            http = fetch_http_info(target, perf)
            result["framework"] = detect_framework(http)
            result["version"] = detect_version(http, result["framework"])

    if "FULL" in scans or "2" in scans:
        logger.info("scan: subdomains")
        with profile("subdomain_scan", timings):
            result["subdomains"] = asyncio.run(
                enumerate_subdomains_async(target, perf, stats)
            )

    if "FULL" in scans or "3" in scans:
        logger.info("scan: ports")
        with profile("port_scan", timings):
            result["ports"] = asyncio.run(
                scan_ports_async(target, perf, stats)
            )

    if "FULL" in scans or "4" in scans:
        logger.info("scan: service inference")
        result["services"] = infer_services(
            result.get("ports", []),
            target
        )

    if "FULL" in scans or "5" in scans:
        logger.info("scan: tls")
        result["tls"] = scan_tls(target)

    if "FULL" in scans or "6" in scans:
        logger.info("scan: security headers")
        if http is None:
            http = fetch_http_info(target, perf)
        result["security_headers"] = analyze_security_headers(http)

    if "FULL" in scans or "7" in scans:
        logger.info("scan: tech stack")
        if http is None:
            http = fetch_http_info(target, perf)
        result["tech_stack"] = summarize_tech_stack(http, result)

    timings["total"] = round(time.perf_counter() - total_start, 3)

    output = {
        "metadata": metadata,
        "timing": timings,
        "async_stats": stats,
        "result": result
    }

    # =========================
    # OPTIONS
    # =========================

    # diff — 이번 스캔을 history에 저장하기 *전에* 계산해야
    # 기존에 저장된 가장 최근 스냅샷과 비교된다 (자기 자신과 비교되는 것 방지)
    if "FULL" in options or "1" in options:
        logger.info("option: diff against last scan")
        diff = diff_last_scan(target, output)
        if diff:
            summary = summarize_diff(diff)
            md = format_diff_markdown(summary)
            output["diff"] = {
                "enabled": True,
                "summary": summary,
                "markdown": md,
                "raw": json.loads(diff.to_json())  # DeepDiff can hold raw `type` objects (type_changes); to_json() makes it JSON-safe
            }
            with open(os.path.join(report_dir, "diff_summary.md"), "w", encoding="utf-8") as f:
                f.write(md)
        else:
            output["diff"] = {
                "enabled": False,
                "summary": [],
                "markdown": "",
                "raw": None
            }

    # 스캔 이력 저장
    if "FULL" in options or "2" in options:
        logger.info("option: save snapshot")
        save_snapshot(target, output)

    # 장기 트렌드 분석
    if "FULL" in options or "4" in options:
        logger.info("option: trend analysis")
        trend = analyze_trends(target)
        output["trend"] = trend

        with open(os.path.join(report_dir, "trend_report.md"), "w", encoding="utf-8") as f:
            f.write(generate_trend_markdown(trend))

        scans_history = load_history(target)
        if scans_history:
            dates, ports, subs = extract_timeseries(scans_history)
            plot_trend(
                dates, ports,
                "Open Ports Over Time",
                "Number of Open Ports",
                os.path.join(report_dir, "ports_trend.png")
            )
            plot_trend(
                dates, subs,
                "Subdomains Over Time",
                "Number of Subdomains",
                os.path.join(report_dir, "subdomains_trend.png")
            )

    # AI 위험 설명 (STUB)
    if "FULL" in options or "5" in options:
        if "trend" in output and "risk_assessment" in output["trend"]:
            output["ai_explanation"] = explain_risk_natural_language(
                output["trend"]["risk_assessment"]
            )

    # =========================
    # OUTPUT
    # =========================

    result_path = os.path.join(report_dir, "result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"done in {timings['total']}s -> {result_path}")
    print("\n[+] Scan completed successfully")


if __name__ == "__main__":
    main()
