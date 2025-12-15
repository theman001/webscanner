from collections import defaultdict

def init_stats():
    return defaultdict(lambda: {"success":0,"timeout":0,"error":0})

def record_success(stats, k): stats[k]["success"]+=1
def record_timeout(stats, k): stats[k]["timeout"]+=1
def record_error(stats, k): stats[k]["error"]+=1
