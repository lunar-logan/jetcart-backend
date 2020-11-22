from marshmallow import ValidationError

from jetcart.service import tax as service
from flask import request, jsonify, Blueprint

blueprint = Blueprint('tax', __name__)


@blueprint.route('/tax', methods=['POST', 'GET', 'DELETE'])
def create_tax():
    if request.method == 'POST':
        tax_data = service.create_tax(**request.get_json())
        return jsonify(**tax_data)
    elif request.method == 'GET':
        return jsonify(service.fetch_all_taxes())
    elif request.method == 'DELETE':
        service.delete_all()
        return jsonify()
    return jsonify(), 405


@blueprint.route('/tax/<tax_type>', methods=['GET'])
def fetch_tax(tax_type: str):
    tax = service.fetch_tax(tax_type)
    return jsonify(**tax)


@blueprint.route('/tax/mapping', methods=['POST', 'GET'])
def crud_tax_mapping():
    if request.method == 'POST':
        mapping = service.create_tax_mapping(**request.get_json())
        return jsonify(**mapping)
    elif request.method == 'GET':
        return jsonify(service.fetch_all_tax_mappings())
    return jsonify(), 405


@blueprint.errorhandler(Exception)
def error_handler(error):
    if isinstance(error, ValidationError):
        return jsonify(message=error.messages), getattr(error, 'status_code', 500)
    elif isinstance(error, ValueError):
        return jsonify(message=str(error)), 400
    return jsonify(message=str(error)), getattr(error, 'status_code', 500)
