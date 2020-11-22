from typing import Dict, List, Any

from marshmallow import Schema, fields, validate, ValidationError

from jetcart.domain import cart
from jetcart.service import catalog as catalog_service
from jetcart.service import oms as order_service
import logging


class CartItemSchema(Schema):
    sku = fields.Str(required=True)
    quantity = fields.Int(required=True)
    unit_price = fields.Float(required=True)


class CartSchema(Schema):
    items = fields.List(
        fields.Nested(CartItemSchema),
        required=True,
        validate=validate.Length(min=1)
    )


def create_cart(**kwargs) -> Dict:
    try:
        result = CartSchema().load(kwargs)
        cart_obj = cart.create_cart(**result)
        return cart_obj.as_dict()
    except ValidationError as err:
        err.status_code = 400
        raise err


def fetch_cart(cart_id: str) -> Dict:
    cart_dict = cart.get_cart_by_id(cart_id).as_dict()
    for item in cart_dict['items']:
        sku = item['sku']
        inv = catalog_service.fetch_inventory(sku)
        product = catalog_service.fetch_product(inv.get('product_id'))
        item['title'] = product['title']
        item['image'] = product.get('images')[0]
    return cart_dict


def add_items(cart_id: str, items: List[Dict]) -> Dict:
    try:
        logging.error(f'cart items: {items}')
        new_items = [
            CartItemSchema().load(item)
            for item in items
        ]
        return cart.add_items_to_cart(
            cart_id,
            new_items
        ).as_dict()
    except ValidationError as err:
        err.status_code = 400
        raise err


def checkout(cart_id: str) -> Dict:
    cart_obj = cart.get_cart_by_id(cart_id)
    if cart_obj:
        if cart_obj.state == cart.CART_STATE_CHECKED_OUT:
            raise ValueError(f'Cart {cart_id} already checked out')

        order = order_service.create_order(cart_id)
        cart_obj.state = cart.CART_STATE_CHECKED_OUT
        cart_obj.save()
        return order

    raise ValueError(f'Invalid cart ID {cart_id}')
