import asyncio
import dns.asyncresolver
from urllib.parse import urlparse
from core.stats import record_success, record_timeout, record_error

async def _resolve(resolver, fqdn, timeout, stats):
    try:
        await asyncio.wait_for(resolver.resolve(fqdn, "A"), timeout)
        record_success(stats, "dns")
        return fqdn
    except asyncio.TimeoutError:
        record_timeout(stats, "dns")
    except Exception:
        record_error(stats, "dns")
    return None

async def enumerate_subdomains_async(url, perf, stats):
    domain = urlparse(url).hostname
    resolver = dns.asyncresolver.Resolver()
    resolver.lifetime = perf["dns_timeout"]

    with open("data/subdomains.txt") as f:
        words = [w.strip() for w in f if w.strip()]

    sem = asyncio.Semaphore(int(perf["concurrency"]))
    tasks = []

    async def runner(w):
        async with sem:
            return await _resolve(
                resolver, f"{w}.{domain}", perf["dns_timeout"], stats
            )

    for w in words:
        tasks.append(runner(w))

    res = await asyncio.gather(*tasks)
    return [r for r in res if r]
