import json
import asyncio
import time
from datetime import datetime

from core.utils import (
    validate_url,
    safe_select,
    configure_performance,
    init_logger
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

def select_options():
    print("""
[ OPTIONS ]
--------------------------------
1. Scan history diff
2. Save scan snapshot
3. Record metadata
4. Configure scan performance
5. Long-term trend analysis
6. AI risk explanation
7. FULL OPTIONS
--------------------------------
""")
    return safe_select(
        prompt="Select options: ",
        valid_choices={"1", "2", "3", "4", "5", "6", "7"},
        full_value="7"
    )


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
        valid_choices={"1", "2", "3", "4", "5", "6", "7", "8"},
        full_value="8"
    )


# =========================
# Main
# =========================

def main():
    logger = init_logger()

    # 1️⃣ URL 입력
    target = input_target_url()

    # 2️⃣ 옵션 / 스캔 선택
    options = select_options()
    scans = select_scans()

    # 3️⃣ 성능 설정
    perf = None
    if "FULL" in options or "4" in options:
        perf = configure_performance()

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
        with profile("framework_scan", timings):
            http = fetch_http_info(target, perf)
            result["framework"] = detect_framework(http)
            result["version"] = detect_version(http, result["framework"])

    if "FULL" in scans or "2" in scans:
        with profile("subdomain_scan", timings):
            result["subdomains"] = asyncio.run(
                enumerate_subdomains_async(target, perf, stats)
            )

    if "FULL" in scans or "3" in scans:
        with profile("port_scan", timings):
            result["ports"] = asyncio.run(
                scan_ports_async(target, perf, stats)
            )

    if "FULL" in scans or "4" in scans:
        result["services"] = infer_services(
            result.get("ports", []),
            target
        )

    if "FULL" in scans or "5" in scans:
        result["tls"] = scan_tls(target)

    if "FULL" in scans or "6" in scans:
        if http is None:
            http = fetch_http_info(target, perf)
        result["security_headers"] = analyze_security_headers(http)

    if "FULL" in scans or "7" in scans:
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

    # 스캔 이력 저장
    if "FULL" in options or "2" in options:
        save_snapshot(output)

    # diff
    if "FULL" in options or "1" in options:
        diff = diff_last_scan(output)
        if diff:
            summary = summarize_diff(diff)
            md = format_diff_markdown(summary)
            output["diff"] = {
                "enabled": True,
                "summary": summary,
                "markdown": md,
                "raw": diff
            }
            with open("report/diff_summary.md", "w", encoding="utf-8") as f:
                f.write(md)
        else:
            output["diff"] = {
                "enabled": False,
                "summary": [],
                "markdown": "",
                "raw": None
            }

    # 장기 트렌드 분석
    if "FULL" in options or "5" in options:
        trend = analyze_trends()
        output["trend"] = trend

        with open("report/trend_report.md", "w", encoding="utf-8") as f:
            f.write(generate_trend_markdown(trend))

        scans_history = load_history()
        if scans_history:
            dates, ports, subs = extract_timeseries(scans_history)
            plot_trend(
                dates, ports,
                "Open Ports Over Time",
                "Number of Open Ports",
                "report/ports_trend.png"
            )
            plot_trend(
                dates, subs,
                "Subdomains Over Time",
                "Number of Subdomains",
                "report/subdomains_trend.png"
            )

    # AI 위험 설명 (STUB)
    if "FULL" in options or "6" in options:
        if "trend" in output and "risk_assessment" in output["trend"]:
            output["ai_explanation"] = explain_risk_natural_language(
                output["trend"]["risk_assessment"]
            )

    # =========================
    # OUTPUT
    # =========================

    with open("report/result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n[+] Scan completed successfully")


if __name__ == "__main__":
    main()
