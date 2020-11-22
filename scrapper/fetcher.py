import logging
from time import time
from typing import Union, Dict

import requests
from mongoengine import connect, Document, StringField, IntField

from scrapper.extractor import FlipkartPDPParser, FlipkartPLPExtractor

connect('nobita')


class Resource(Document):
    url = StringField(primary_key=True, required=True)
    body = StringField()


def fetch_network(url: str) -> Union[str, None]:
    r = requests.get(url)
    logging.error(f"{url} - {r.status_code} - {r.headers.get('content-length')}")
    if r.status_code / 100 == 2:
        return r.text
    return None


def fetch(url: str) -> str:
    resource = Resource.objects(url=url).first()
    if not resource:
        content = fetch_network(url)
        if content:
            r = Resource(url=url, body=content)
            r.save()
            return r.body

    return resource.body

# from flask import Flask, render_template, request

# app = Flask(__name__)

pdp_parser = FlipkartPDPParser()
plp_parser = FlipkartPLPExtractor()

CATALOG_BASE_URL = "http://localhost:5000/product"

PLP_URLs = [
]

import time


def extract(plp_url):
    html = fetch_network(plp_url)
    pdp_links = plp_parser.extract(html) or []
    for a_link in pdp_links:
        time.sleep(get_sleep_interval(5))
        try:
            product_data = pdp_parser.extract(fetch_network(a_link))
            add_to_catalog(product_data)
        except Exception:
            logging.error(f"Exception extracting PDP url {a_link}", exc_info=True)


class Sequence(Document):
    name = StringField(primary_key=True, required=True)
    value = IntField(required=True, default=1)


def add_to_catalog(body: Dict):
    r = requests.post(CATALOG_BASE_URL, json=dict(
        # id=str(_get_sequence("catalog.product")),
        title=body['title'],
        description=body['description'],
        category=body['category'][1],
        images=body['images'],
        price=float(body['price'][1:]),
        mrp=float(body['price'][1:])
    ))
    logging.error(f"{CATALOG_BASE_URL} - {r.status_code}")


def _get_sequence(name: str):
    seq = Sequence.objects(name=name).first()
    if not seq:
        seq = Sequence(name=name)
        seq.save()
    cur_val = seq.value
    seq.value += 1
    seq.save()
    return cur_val


import random


def get_sleep_interval(base_time=5):
    return base_time + random.randint(1, base_time)


for plp_url in PLP_URLs:
    extract(plp_url)

#
# #
# @app.route('/', methods=['GET'])
# def extract():
#     pdp_url = request.args.get('pdpUrl')
#     if pdp_url:
#         body = pdp_parser.extract(fetch(pdp_url))
#     else:
#         body = {}
#     print(body)
#     body['pdpUrl'] = pdp_url
#     body['json'] = json.dumps(body, indent=2)
#     r = requests.post(CATALOG_BASE_URL, json=dict(
#         title=body['title'],
#         description=body['description'],
#         category=body['category'][1],
#         images=body['images'],
#         price=float(body['price'][1:]),
#         mrp=float(body['price'][1:])
#     ))
#     body['status_code'] = r.status_code
#     body['response'] = r.text
#     return render_template('extractor.html', **body), 200
#

# #
# if __name__ == '__main__':
#     app.run(port=5050, debug=True)
