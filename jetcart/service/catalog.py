import collections
from typing import Dict, List, Union

from jetcart.domain import catalog


def create_product(**kwargs) -> Dict:
    return catalog.create_product(**kwargs).as_dict()


def fetch_product(product_id: str) -> Union[Dict, None]:
    product = catalog.get_product_by_id(product_id)
    if product:
        return product.as_dict()
    return None


def fetch_all_products_by_cat(cat: str, page: int, size: int) -> List[Dict]:
    return [
        prod.as_dict()
        for prod in catalog.get_all_products_by_cat(cat, page, size)
    ]


def sanitize_kwargs(kwargs: Dict) -> Dict:
    return {
        'title': kwargs.get('title'),
        'filters': kwargs.get('filters') or {}
    }


import logging


def search_products(**kwargs) -> Dict:
    kwargs = sanitize_kwargs(kwargs)
    logging.error(f'{kwargs}')
    products = [
        product.as_dict()
        for product in catalog.search_products(**kwargs)
    ]
    return dict(
        facets=compute_facets(products),
        products=products
    )


def compute_facets(products: List[Dict]) -> Dict[str, int]:
    coll = collections.Counter()
    for product in products:
        coll[product['category']] += 1
    return coll


def fetch_all_products(page: int, size: int) -> List[Dict]:
    return [
        p.as_dict()
        for p in catalog.get_all_products(page, size)
    ]


def delete_all_products() -> None:
    catalog.delete_all_products()


def create_warehouse(**kwargs) -> Dict:
    return catalog.create_warehouse(**kwargs).as_dict()


def fetch_warehouse(warehouse_id: str) -> Dict:
    return catalog.get_warehouse_by_id(warehouse_id).as_dict()


def create_inventory(**kwargs) -> Dict:
    return catalog.create_inventory(**kwargs).as_dict()


def fetch_inventory(sku: str) -> Dict:
    return catalog.get_inventory_by_id(sku).as_dict()


def block_inventory(sku: str, quantity: int):
    return
