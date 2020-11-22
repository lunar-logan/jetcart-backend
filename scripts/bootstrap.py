import requests


def get_all_products():
    r = requests.get('http://localhost:5000/product?page=0&size=50000')
    return r.json()


def define_taxes():
    categories = [
        prod_data.get('category')
        for prod_data in get_all_products()
    ]

    tax_mapping_url = "http://localhost:5000//tax/mapping"
    for cat in categories:
        r = requests.post(tax_mapping_url, json={
            'category': cat,
            'taxes': ["C_GST", "S_GST"]
        })
        print(cat, r.status_code)

define_taxes()