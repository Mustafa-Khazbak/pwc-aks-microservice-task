from flask import Blueprint, jsonify

health_blueprint = Blueprint('health_blueprint', __name__)

@health_blueprint.route('/health', methods=['GET'])
def health():
    # Simple health check — you can extend this later
    return jsonify({"status": "healthy"}), 200
