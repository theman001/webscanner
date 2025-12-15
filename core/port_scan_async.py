import asyncio
from urllib.parse import urlparse
from core.stats import record_success, record_timeout, record_error

COMMON_PORTS = [21,22,80,443,8080,8443,3306,3389]

async def _check(host, port, timeout, stats):
    try:
        r, w = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout
        )
        w.close()
        await w.wait_closed()
        record_success(stats, "ports")
        return port
    except asyncio.TimeoutError:
        record_timeout(stats, "ports")
    except Exception:
        record_error(stats, "ports")
    return None

async def scan_ports_async(url, perf, stats):
    host = urlparse(url).hostname
    sem = asyncio.Semaphore(int(perf["concurrency"]))

    async def runner(p):
        async with sem:
            return await _check(host, p, perf["port_timeout"], stats)

    res = await asyncio.gather(*(runner(p) for p in COMMON_PORTS))
    return [p for p in res if p]
