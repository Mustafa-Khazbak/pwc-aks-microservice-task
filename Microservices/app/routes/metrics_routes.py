from flask import Blueprint
from app.services.metrics_service import get_metrics

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/metrics')
def metrics():
    return get_metrics()
