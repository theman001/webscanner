import sys, json, asyncio, time
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
from core.trend_analyzer import analyze_trends, extract_timeseries, load_history
from core.trend_reporter import generate_trend_markdown
from core.trend_graph import plot_trend
from core.ai_explainer import explain_risk_natural_language

def select_options():
    print("""
[ OPTIONS ]
1. Scan history diff
2. Save scan snapshot
3. Record metadata
4. Configure scan performance
5. Long-term trend analysis
6. AI risk explanation
7. FULL OPTIONS
""")
    return safe_select(
        "Select options: ",
        valid_choices={"1","2","3","4","5","6","7"},
        full_value="7"
    )

def select_scans():
    print("""
[ SCANS ]
1. Web framework & version
2. Subdomain scan
3. Port scan
4. Port → service inference
5. TLS / certificate
6. Security headers
7. Technology stack summary
8. FULL SCAN
""")
    return safe_select(
        "Select scans: ",
        valid_choices={"1","2","3","4","5","6","7","8"},
        full_value="8"
    )

def main():
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <url>")
        sys.exit(1)

    target = sys.argv[1]
    validate_url(target)
    logger = init_logger()

    options = select_options()
    scans = select_scans()

    perf = configure_performance() if ("4" in options or "FULL" in options) else None
    stats = init_stats()
    timings = {}

    result = {}
    meta = {
        "timestamp": datetime.now().isoformat(),
        "options_selected": list(options),
        "scans_selected": list(scans),
        "performance": perf
    }

    start_total = time.perf_counter()

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
        result["services"] = infer_services(result.get("ports", []), target)

    if "FULL" in scans or "5" in scans:
        result["tls"] = scan_tls(target)

    if "FULL" in scans or "6" in scans:
        result["security_headers"] = analyze_security_headers(http)

    if "FULL" in scans or "7" in scans:
        result["tech_stack"] = summarize_tech_stack(http, result)

    timings["total"] = round(time.perf_counter() - start_total, 3)

    output = {
        "metadata": meta,
        "timing": timings,
        "async_stats": stats,
        "result": result
    }

    if "2" in options or "FULL" in options:
        save_snapshot(output)

    if "1" in options or "FULL" in options:
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
            open("report/diff_summary.md","w",encoding="utf-8").write(md)

    if "5" in options or "FULL" in options:
        trend = analyze_trends()
        output["trend"] = trend
        open("report/trend_report.md","w",encoding="utf-8").write(
            generate_trend_markdown(trend)
        )

        scans = load_history()
        dates, ports, subs = extract_timeseries(scans)
        plot_trend(dates, ports, "Open Ports Over Time", "Ports", "report/ports_trend.png")
        plot_trend(dates, subs, "Subdomains Over Time", "Subdomains", "report/subdomains_trend.png")

    if "6" in options or "FULL" in options:
        if "trend" in output:
            output["ai_explanation"] = explain_risk_natural_language(
                output["trend"]["risk_assessment"]
            )

    open("report/result.json","w",encoding="utf-8").write(
        json.dumps(output, indent=2, ensure_ascii=False)
    )

    print("[+] Scan completed")

if __name__ == "__main__":
    main()
