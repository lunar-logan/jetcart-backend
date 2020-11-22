from typing import Dict
from jetcart.domain import oms
from jetcart.service import cart as cart_service


def create_order(cart_id: str) -> Dict:
    order = oms.create_order(cart_id)
    if order:
        return order.as_dict()
    raise ValueError(f'Invalid cart id {cart_id}')


def fetch_order(order_id: str) -> Dict:
    order = oms.get_order_by_id(order_id)
    if order:
        cart = cart_service.fetch_cart(order.cart_id)
        order_obj = order.as_dict()
        order_obj['cart'] = cart
        return order_obj


import logging


def place_order(order_id: str, **kwargs) -> Dict:
    logging.error(f'order ID={order_id} kwargs={kwargs}')
    return oms.update_order(order_id, **kwargs).as_dict()
