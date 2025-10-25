from flask import Flask, request, current_app
from app.routes.user_routes import user_blueprint
from app.routes.product_routes import product_blueprint
from app.routes.metrics_routes import metrics_bp
from prometheus_flask_exporter import PrometheusMetrics
from app.services.logging_service import setup_logging
from app.routes.health_routes import health_blueprint


def create_app():
    app = Flask(__name__)

    # Prometheus Integration
    metrics = PrometheusMetrics(app)
    metrics.info("app_info", "Application info", version="1.0.0")

    # Structured Logging
    setup_logging(app)

    # Request Lifecycle Hooks
    @app.before_request
    def log_request_info():
        current_app.logger.info("Incoming request", extra={
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr
        })

    @app.after_request
    def log_response_info(response):
        current_app.logger.info("Outgoing response", extra={
            "status": response.status_code,
            "path": request.path
        })
        return response

    # --- Register Blueprints ---
    app.register_blueprint(user_blueprint)
    app.register_blueprint(product_blueprint)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(health_blueprint)

    return app
