import enum
import json
from typing import List, Dict

import arrow
from mongoengine import Document, StringField, FloatField, DictField, IntField, ReferenceField, LongField, ListField


class Product(Document):
    title = StringField(required=True)
    description = StringField()
    price = FloatField(required=True)
    mrp = FloatField(required=True)
    category = StringField(required=True)
    attrs = DictField()
    images = ListField(field=StringField())
    sales_tax = FloatField(required=False, default=18)

    meta = {
        'indexes': [
            {
                'fields': ['$title'],
                'default_language': 'english'
            }
        ]
    }

    def as_dict(self):
        return dict(
            id=str(self.id),
            title=self.title,
            description=self.description,
            category=self.category,
            price=self.price,
            mrp=self.mrp,
            attrs=self.attrs,
            images=[
                str(img)
                for img in self.images
            ]
        )


class Warehouse(Document):
    code = StringField(primary_key=True)
    name = StringField(required=True)
    lat = FloatField()
    lng = FloatField()

    def as_dict(self):
        return dict(
            code=self.code,
            name=self.name
        )


class Inventory(Document):
    sku = StringField(primary_key=True)
    product = ReferenceField(Product)
    warehouse = ReferenceField(Warehouse)
    quantity = IntField(required=True, min_value=0)
    buyer_limit = IntField(required=False, min_value=1, default=3)

    def as_dict(self):
        return dict(
            sku=str(self.sku),
            product_id=str(self.product.id),
            warehouse_id=str(self.warehouse.id),
            quantity=self.quantity
        )


class BlockedInventoryState(enum.Enum):
    BLOCKED = "blocked"
    COMMITTED = "committed"


class BlockedInventory(Document):
    sku = StringField(required=True)
    quantity = IntField(required=True)
    expiry = LongField(required=True)
    state = StringField(required=True)


class NotEnoughInventory(Exception):
    pass


class BlockedInventoryExpired(Exception):
    pass


def create_product(**kwargs) -> Product:
    p = Product(**kwargs)
    p.save()
    return p


def get_product_by_id(product_id: str) -> Product:
    return Product.objects(id=product_id).first()


def get_all_products_by_cat(cat: str, page: int = 0, size: int = 20) -> List[Product]:
    return Product.objects(category=cat)[page * size:page * size + size]


def search_products(filters: Dict, title: str) -> List[Product]:
    filters = json.loads(filters or '{}')
    if title:
        return Product.objects(**filters).search_text(title).order_by('$text_score')
    elif filters:
        return Product.objects(**filters)
    return get_all_products(0, 1000)


def get_all_products(page: int = 0, size: int = 10) -> List[Product]:
    return Product.objects[page * size:page * size + size]


def delete_all_products() -> None:
    Product.objects.delete()


def create_warehouse(**kwargs) -> Warehouse:
    warehouse = Warehouse(
        code=kwargs['code'],
        name=kwargs['name']
    )
    warehouse.save()
    return warehouse


def get_warehouse_by_id(warehouse_id: str) -> Warehouse:
    return Warehouse.objects(pk=warehouse_id).first()


def create_inventory(**kwargs) -> Inventory:
    inv = Inventory(
        sku=kwargs['sku'],
        product=get_product_by_id(kwargs['product_id']),
        warehouse=get_warehouse_by_id(kwargs['warehouse_id']),
        quantity=kwargs['quantity']
    )
    inv.save()
    return inv


def update_inventory(sku: str, quantity: int) -> Inventory:
    inv = get_inventory_by_id(sku)
    inv.quantity = quantity
    inv.save()
    return inv


def get_inventory_by_id(sku: str) -> Inventory:
    return Inventory.objects(sku=sku).first()


def block_inventory(sku: str, quantity: int) -> str:
    inventory = get_inventory_by_id(sku)
    if not inventory:
        raise ValueError(f"Invalid SKU [{sku}]")

    if quantity <= 0 or quantity > inventory.buyer_limit:
        raise ValueError(f"0 < quantity <= {inventory.buyer_limit}")

    if inventory.quantity > quantity:
        block_inv = BlockedInventory(
            sku=sku,
            quantity=quantity,
            expiry=_expiry_time(),
            state=str(BlockedInventoryState.BLOCKED)
        )
        block_inv.save()

        inventory.quantity -= quantity
        inventory.save()
        return str(block_inv.id)
    raise NotEnoughInventory


def _expiry_time(delta_minutes=5):
    return arrow.utcnow().shift(minutes=delta_minutes).timestamp


def get_blocked_inventory_by_id(id: str) -> BlockedInventory:
    return BlockedInventory.objects(id=id).first()


def commit_inventory(blocked_inv_id: str):
    blocked = get_blocked_inventory_by_id(blocked_inv_id)
    if not blocked:
        raise ValueError(f"Unknown blocked inventory id {blocked_inv_id}")

    # Make sure the blocked inventory has not expired
    if arrow.utcnow().timestamp <= blocked.expiry:
        inv = get_inventory_by_id(blocked.sku)
        inv.quantity -= blocked.quantity
        inv.save()

        blocked.state = str(BlockedInventoryState.COMMITTED)
        blocked.save()

    raise BlockedInventoryExpired
