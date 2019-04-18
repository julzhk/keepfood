import os
import pprint

import requests


class ProductNotFoundException(Exception):
    pass


class _UPC_lookup(object):
    url = ''

    def __init__(self, upc):
        self.upc = upc

    def do_json_request(self):
        print(self.__class__.__name__)
        print('- ' * 8)
        print(self.__dict__)
        instance_vars = self.__dict__
        class_vars = self.__class__.__dict__
        all_atributes = {**class_vars, **instance_vars}
        filtered_attributes = {k: str(v) for (k, v) in all_atributes.items() if not k[0] == '_'}
        url = self.url.format(**filtered_attributes)
        print(url)
        response = requests.get(url,
                                headers={
                                    'cache-control': "no-cache"
                                })
        self.product_data = response.json()
        pprint.pprint(self.product_data)
        print("-" * 8)
        return self.product_data

    def post_process(self, data):
        return data

    def execute(self):
        d = self.do_json_request()
        try:
            return self.post_process(d)
        except Exception as err:
            print('post process error')
            print(d)
            raise err


class open_food_facts_API(_UPC_lookup):
    url = 'https://world.openfoodfacts.org/api/v0/product/{upc}.json'

    def post_process(self, data):
        if data.get('status', 'success') == 0:
            raise ProductNotFoundException()
        product_data = {
            'title': data['product']['product_name'],
            'description': data['product']['product_name'],
            'upcnumber': self.upc
        }
        return product_data


class upc_database_API(_UPC_lookup):
    key = os.environ.get('UPC_KEY', 'No_UPC_KEY')
    url = 'https://api.upcdatabase.org/product/{upc}/{key}'

    def post_process(self, data):
        product_data = {
            'title': data['title'],
            'description': data['description'],
            'upcnumber': data['upcnumber'],
        }
        return product_data


class EAN_lookup(_UPC_lookup):
    url = "https://eandata.com/feed/?v=3&keycode={key}&mode=json&find={upc}&comp=no&get=all"
    key = os.environ.get('EAN_KEY', 'No_EAN_KEY')

    def post_process(self, data):
        title = data.get('product').get('attributes', {}).get('product', '-')
        product_data = {
            'title': title,
            'description': '',
            'upcnumber': self.upc
        }
        return product_data


class Ean_Search_API(_UPC_lookup):
    url = "https://api.ean-search.org/api?token={key}&format=json&lang=1"
    key = os.environ.get('EAN_SEARCH_KEY', 'No_EAN_SEARCH_KEY')

    def post_process(self, data):
        if "error" in data[0]:
            raise ProductNotFoundException()
        name = data[0]["name"]
        product_data = {
            'title': name,
            'description': name,
            'upcnumber': self.upc
        }
        return product_data
