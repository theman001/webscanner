def infer_services(ports, url):
    services = []
    for p in ports:
        if p in (443, 8443):
            services.append({"port": p, "service": "https"})
        elif p in (80, 8080):
            services.append({"port": p, "service": "http"})
        else:
            services.append({"port": p, "service": "unknown"})
    return services
