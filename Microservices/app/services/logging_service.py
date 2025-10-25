import logging
import json_log_formatter

def setup_logging(app):
    formatter = json_log_formatter.JSONFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    app.logger.info("Application logging initialized")