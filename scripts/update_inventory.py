

import requests


r = requests.get('http://localhost:5000/product?page=0&size=50000')
print(r.status_code)
for product_data in r.json():
    inventory = dict(
        sku=product_data['id'],
        product_id=product_data['id'],
        warehouse_id="WMS1",
        quantity=100
    )
    r = requests.post('http://localhost:5000/v1/inventory', json=inventory)
    print(r.status_code, r.json())
    print('-'*80)