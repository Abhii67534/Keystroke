def extract_network_features(session):
    return [
        session["session_duration"],
        session["avg_packet_size"],
        session["total_packets"],
        session["dns_queries"],
        session["http_ratio"],
        session["https_ratio"]
    ]