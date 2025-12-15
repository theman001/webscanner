import time
from contextlib import contextmanager

@contextmanager
def profile(name, store):
    s = time.perf_counter()
    yield
    store[name] = round(time.perf_counter()-s,3)
