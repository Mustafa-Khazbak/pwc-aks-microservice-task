from flask import Blueprint, jsonify
from app.services.product_service import ProductService
from prometheus_client import Summary

product_blueprint = Blueprint('product_blueprint', __name__)
product_service = ProductService()

# Custom metric: measure how long /products takes to respond
product_processing_time = Summary(
    'product_processing_seconds',
    'Time spent processing the /products endpoint'
)

@product_blueprint.route('/products', methods=['GET'])
@product_processing_time.time()
def get_products():
    products = product_service.get_products()
    return jsonify(products), 200

@product_blueprint.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = product_service.get_product_by_id(product_id)
    if product:
        return jsonify(product), 200
    else:
        return jsonify({"message": "Product not found"}), 404
