import abc
from typing import Dict, List, Union

from mongoengine import Document, EmbeddedDocument, StringField, IntField, FloatField, \
    EmbeddedDocumentListField, EmbeddedDocumentField

from jetcart.service import catalog as catalog_service
from jetcart.service import tax as tax_service


class CartItem(EmbeddedDocument):
    sku = StringField(required=True)
    quantity = IntField(required=True)
    unit_price = FloatField(required=True)
    sales_tax_type = StringField()
    unit_sales_tax = FloatField(default=0)

    def as_dict(self):
        return dict(
            sku=self.sku,
            quantity=self.quantity,
            unit_price=self.unit_price,
            sales_tax_type=self.sales_tax_type,
            unit_sales_tax=self.unit_sales_tax
        )

    def merge(self, other: 'CartItem') -> Union['CartItem', None]:
        if other.sku == self.sku and other.unit_price == self.unit_price:
            return CartItem(
                sku=self.sku,
                unit_price=self.unit_price,
                quantity=self.quantity + other.quantity
            )
        return None


class CartCalculation(EmbeddedDocument):
    total_value = FloatField(required=True)
    total_discount = FloatField(default=0)
    total_sales_tax = FloatField(required=True)
    total_payable_amount = FloatField(required=True)

    def as_dict(self) -> Dict:
        return dict(
            total_value=self.total_value,
            total_discount=self.total_discount,
            total_sales_tax=self.total_sales_tax,
            total_payable_amount=self.total_payable_amount
        )


CART_STATE_CREATED = 0
CART_STATE_CHECKED_OUT = 2


class Cart(Document):
    items = EmbeddedDocumentListField(document_type=CartItem, required=True)
    value = EmbeddedDocumentField(document_type=CartCalculation, required=False)
    state = IntField(default=CART_STATE_CREATED)

    def as_dict(self):
        return dict(
            id=str(self.id),
            items=[
                item.as_dict()
                for item in self.items
            ],
            value=self.value.as_dict(),
            state=self.state
        )

    def calculate(self, calculator_value_calc: 'CartValueCalculator') -> 'CartCalculation':
        """Calculates this cart value"""
        self.value = calculator_value_calc.calculate(self)
        return self.value

    def add_items(self, other_items: List[CartItem]) -> 'Cart':
        if not other_items:
            return self
        # merge items based on the sku and unit_price/discount
        all_items = sorted(
            self.items + other_items,
            key=lambda item: item.sku
        )

        if not all_items:
            return self

        all_merged_items = []
        last_item = all_items[0]
        for an_item in all_items[1:]:
            merged_item = last_item.merge(an_item)
            if merged_item:
                last_item = merged_item
            else:
                all_merged_items.append(last_item)
                last_item = an_item
        all_merged_items.append(last_item)
        self.items = all_merged_items
        return self


class CartValueCalculator:
    @abc.abstractmethod
    def calculate(self, cart: Cart) -> CartCalculation:
        pass


class SimpleCartValueCalculator(CartValueCalculator):
    def calculate(self, cart: Cart) -> CartCalculation:
        sku_tax_map = self._build_sku_tax_map(cart.items)

        total_amount, total_sales_tax, total_discounts = 0, 0, 0
        for item in cart.items:
            taxes = sku_tax_map.get(item.sku) or []
            amount = item.unit_price * item.quantity
            sales_tax = sum(map(lambda tax: tax.get('value', 0) * amount / 100.0, taxes))
            item.unit_sales_tax = sales_tax / item.quantity
            item.sales_tax_type = ','.join(map(lambda tax: tax.get('type'), taxes))
            total_amount += amount
            total_sales_tax += sales_tax

        return CartCalculation(
            total_value=total_amount,
            total_sales_tax=total_sales_tax,
            total_discount=total_discounts,
            total_payable_amount=max(
                0,
                total_amount + total_sales_tax - total_discounts
            )
        )

    @staticmethod
    def _build_sku_tax_map(items: List[CartItem]):
        sku_tax = {}
        for item in items:
            if item.sku not in sku_tax:
                inventory = catalog_service.fetch_inventory(item.sku)
                if inventory and inventory.get('product_id'):
                    product = catalog_service.fetch_product(inventory.get('product_id'))
                    if product and product.get('category'):
                        taxes = tax_service.fetch_tax_by_category(product.get('category'))
                        if taxes:
                            sku_tax[item.sku] = taxes
        return sku_tax


cart_value_calculator = SimpleCartValueCalculator()


def create_cart(**kwargs) -> Cart:
    cart = Cart(items=[
        CartItem(**item)
        for item in kwargs['items']
    ])
    cart.calculate(cart_value_calculator)
    cart.save()
    return cart


def get_cart_by_id(cart_id: str) -> Cart:
    return Cart.objects(id=cart_id).first()


def add_items_to_cart(cart_id: str, items: List[Dict]) -> Cart:
    cart = get_cart_by_id(cart_id)
    if not cart:
        raise ValueError(f"No cart for ID [{cart_id}]")

    if not items:
        return cart

    new_cart_items = [
        CartItem(**item)
        for item in items
    ]
    cart.add_items(new_cart_items)
    cart.calculate(cart_value_calculator)
    cart.save()
    return cart


def update_cart(cart_id: str, sku: str, quantity: int):
    pass
