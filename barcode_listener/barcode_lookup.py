import os
import pprint

import requests


class UPC_lookup(object):
    url = ''

    def __init__(self, upc):
        self.upc = upc

    def do_json_request(self):
        print(self.__dict__)
        instance_vars = self.__dict__
        class_vars = self.__class__.__dict__
        all_atributes = {**class_vars, **instance_vars}
        filtered_attributes = {k: str(v) for (k, v) in all_atributes.items() if not k[0] == '_'}
        url = self.url.format(**filtered_attributes)
        print(url)
        response = requests.request("GET",
                                    url,
                                    headers={'cache-control': "no-cache", })
        self.product_data = response.json()
        pprint.pprint(self.product_data)
        print("-" * 8)
        return self.product_data

    def post_process(self, data):
        return data

    def execute(self):
        d = self.do_json_request()
        return self.post_process(d)


class open_food_facts_API(UPC_lookup):
    url = 'https://world.openfoodfacts.org/api/v0/product/{upc}.json'

    def post_process(self, data):
        product_data = {
            'title': data['product']['product_name'],
            'description': data['product']['product_name'],
            'upcnumber': self.upc
        }
        return product_data


class upc_database_API(UPC_lookup):
    url = '"https://api.upcdatabase.org/product/{upc}/{key}"'
    key = os.environ.get('UPC_KEY', '??')

    def post_process(self, data):
        product_data = {
            'title': data['title'],
            'description': data['description'],
            'upcnumber': data['upcnumber'],
        }
        return product_data


class EAN_lookup(UPC_lookup):
    url = "https://eandata.com/feed/?v=3&keycode={key}&mode=json&find={upc}"
    key = os.environ.get('EAN_KEY', '??')

    def post_process(self, data):
        title = data.get('product')[0].get('attributes', {}).get('product', '-')
        product_data = {
            'title': title,
            'description': '',
            'upcnumber': self.upc
        }
        return product_data
