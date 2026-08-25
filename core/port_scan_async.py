import asyncio
from urllib.parse import urlparse
from core.stats import record_success, record_timeout, record_error

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
    143, 161, 389, 443, 445, 465, 587, 631, 636, 873,
    993, 995, 1080, 1433, 1521, 1723, 2049, 2082, 2083, 2086,
    2087, 2095, 2096, 2181, 2222, 2375, 2376, 3000, 3128, 3306,
    3389, 4000, 4443, 4567, 5000, 5432, 5601, 5672, 5900, 5985,
    5986, 6379, 7001, 8000, 8008, 8080, 8081, 8088, 8090, 8161,
    8443, 8500, 8888, 8983, 9000, 9042, 9092, 9200, 9300, 9418,
    9999, 10000, 11211, 15672, 27017, 27018,
]

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
