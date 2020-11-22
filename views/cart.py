from marshmallow import ValidationError

from jetcart.service import cart as service
from flask import request, jsonify, Blueprint

import logging

blueprint = Blueprint('cart', __name__)


@blueprint.route('/v1/cart', methods=['POST'])
def create_cart():
    cart_dict = service.create_cart(**request.get_json())
    return jsonify(**cart_dict)


@blueprint.route('/v1/cart/<cart_id>', methods=['GET', 'PATCH'])
def get_cart(cart_id: str):
    if request.method == 'GET':
        return jsonify(**service.fetch_cart(cart_id))
    elif request.method == 'PATCH':
        return jsonify(**service.add_items(cart_id, request.get_json()))
    return jsonify(), 405


@blueprint.route('/v1/cart/<cart_id>/checkout', methods=['POST'])
def checkout_cart(cart_id: str):
    order = service.checkout(cart_id)
    return jsonify(**order), 200


@blueprint.errorhandler(Exception)
def error_handler(error):
    logging.error(msg="Exception handling request", exc_info=True)
    if isinstance(error, ValidationError):
        return jsonify(message=error.messages), getattr(error, 'status_code', 500)
    return jsonify(message=str(error)), getattr(error, 'status_code', 500)
