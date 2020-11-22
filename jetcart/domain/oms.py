from datetime import datetime
from typing import Dict

from mongoengine import Document, StringField, EmbeddedDocument, FloatField, EmbeddedDocumentField, \
    IntField, DateTimeField


class PaymentDetail(EmbeddedDocument):
    amount = FloatField(required=True)
    payment_type = StringField(required=True, default="Cash on delivery")

    def as_dict(self) -> Dict:
        return dict(
            amount=self.amount,
            payment_type=self.payment_type
        )


class CustomerDetail(EmbeddedDocument):
    name = StringField(required=True)
    email = StringField(required=True)
    phone = StringField(required=True)

    def as_dict(self) -> Dict:
        return dict(
            name=self.name,
            email=self.email,
            phone=self.phone
        )


class Address(EmbeddedDocument):
    line1 = StringField(required=True)
    line2 = StringField()
    city = StringField(required=True)
    state = StringField(required=True)
    country = StringField(required=True, default="India")
    postal_code = IntField(required=True)

    def as_dict(self) -> Dict:
        return dict(
            line1=self.line1,
            line2=self.line2,
            city=self.city,
            state=self.state,
            country=self.country,
            postal_code=self.postal_code
        )


ORDER_STATE_CREATED = 0
ORDER_STATE_RECEIVED = 5


class Order(Document):
    cart_id = StringField(required=True)
    payment = EmbeddedDocumentField(document_type=PaymentDetail)
    delivery_address = EmbeddedDocumentField(document_type=Address)
    state = IntField(default=ORDER_STATE_CREATED)
    order_date = DateTimeField()
    customer = EmbeddedDocumentField(document_type=CustomerDetail)

    def as_dict(self) -> Dict:
        return dict(
            id=str(self.id),
            cart_id=self.cart_id,
            state=self.state,
            payment=self.payment.as_dict() if self.payment else None,
            delivery_address=self.delivery_address.as_dict() if self.delivery_address else None,
            order_date=self.order_date,
            customer=self.customer.as_dict() if self.customer else None
        )


def create_order(cart_id: str) -> Order:
    order = Order(cart_id=cart_id)
    order.save()
    return order


def update_order(
        order_id: str,
        payment_details: Dict,
        delivery_address: Dict,
        customer: Dict
) -> Order:
    order = get_order_by_id(order_id)
    if order:
        order.delivery_address = Address(**delivery_address)
        order.payment = PaymentDetail(**payment_details)
        order.order_date = datetime.now()
        order.customer = CustomerDetail(**customer)
        order.state = ORDER_STATE_RECEIVED
        order.save()
        return order
    raise ValueError(f'Invalid order id {order_id}')


def update_delivery_address(order_id: str, **kwargs) -> Order:
    order = get_order_by_id(order_id)
    if order:
        order.delivery_address = Address(**kwargs)
        order.save()
        return order
    raise ValueError(f'Invalid order id {order_id}')


def update_payment_address(order_id: str, **kwargs) -> Order:
    order = get_order_by_id(order_id)
    if order:
        order.payment = PaymentDetail(**kwargs)
        order.save()
        return order
    raise ValueError(f'Invalid order id {order_id}')


def get_order_by_id(order_id: str) -> Order:
    return Order.objects(id=order_id).first()


def get_all_orders(mongo_client, page: int = 0, size: int = 10):
    pass


def cancel_order(mongo_client, order_id: str):
    pass
