from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

def get_metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    