from jetcart.service import catalog as service
from flask import request, jsonify, Blueprint

blueprint = Blueprint('catalog', __name__)


@blueprint.route('/product', methods=['POST', 'GET', 'DELETE'])
def create_product():
    if request.method == 'POST':
        product_data = service.create_product(**request.get_json())
        return jsonify(**product_data)
    elif request.method == 'GET':
        products_data = service.fetch_all_products(
            int(request.args.get('page', 0)),
            int(request.args.get('size', 10))
        )
        return jsonify(products_data)
    elif request.method == 'DELETE':
        service.delete_all_products()
        return jsonify(), 200


@blueprint.route('/product/search', methods=['GET'])
def search_products():
    products_data = service.search_products(**request.args)
    return jsonify(products_data), 200


@blueprint.route('/product/<product_id>')
def fetch_product(product_id):
    product_data = service.fetch_product(product_id)
    if product_data:
        return jsonify(**product_data)
    return jsonify(message=f"Unknown Product ID [{product_id}]"), 400


@blueprint.route('/v1/warehouse', methods=['POST'])
def create_warehouse():
    warehouse_data = service.create_warehouse(**request.get_json())
    return jsonify(**warehouse_data)


@blueprint.route('/v1/warehouse/<warehouse_id>')
def fetch_warehouse(warehouse_id):
    return service.fetch_warehouse(warehouse_id)


@blueprint.route('/v1/inventory', methods=['POST'])
def create_inventory():
    inv = service.create_inventory(**request.get_json())
    return jsonify(**inv)


@blueprint.route('/v1/inventory/<sku>')
def fetch_inventory(sku: str):
    inv = service.fetch_inventory(sku)
    return jsonify(**inv)
