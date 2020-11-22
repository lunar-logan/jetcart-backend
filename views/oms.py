from marshmallow import ValidationError

from jetcart.service import cart as service
from jetcart.service import oms as oms_service
from flask import request, jsonify, Blueprint

import logging

blueprint = Blueprint('oms', __name__)


@blueprint.route('/v1/order/<order_id>')
def get_order(order_id: str):
    order = oms_service.fetch_order(order_id)
    if order:
        return jsonify(**order), 200
    return jsonify(), 404


@blueprint.route('/v1/order/<order_id>/place', methods=['POST'])
def place_order(order_id: str):
    order_data = oms_service.place_order(order_id, **request.get_json())
    return jsonify(order_data), 200


@blueprint.errorhandler(Exception)
def error_handler(error):
    logging.error(msg="Exception handling request", exc_info=True)
    if isinstance(error, ValidationError):
        return jsonify(message=error.messages), getattr(error, 'status_code', 500)
    return jsonify(message=str(error)), getattr(error, 'status_code', 500)
