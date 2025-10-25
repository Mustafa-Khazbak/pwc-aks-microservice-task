from flask import Blueprint, jsonify
from prometheus_client import Counter
from app.services.user_service import UserService

user_blueprint = Blueprint('user_blueprint', __name__)
user_service = UserService()

# Custom metric: count how many times /users endpoint is accessed
user_requests_total = Counter(
    'user_requests_total',
    'Total number of times the /users endpoint was called'
)


@user_blueprint.route('/users', methods=['GET'])
def get_users():
    user_requests_total.inc()
    users = user_service.get_users()
    return jsonify(users), 200

@user_blueprint.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"message": "User not found"}), 404
