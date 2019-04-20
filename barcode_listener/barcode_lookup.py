import os
import pprint

import requests


class ProductNotFoundException(Exception):
    pass


class _UPC_lookup(object):
    url = ''
    key = 'No_KEY'
    klass_name = 'Placeholder'

    def __init__(self, upc):
        self.upc = upc

    def do_json_request(self):
        self.klass_name = self.__class__.__name__
        print()
        print('- ' * 8)
        print(self.klass_name)
        print('- ' * 8)
        self.key = os.environ.get(self.key, f'No_{self.klass_name}_KEY')
        instance_vars = self.__dict__
        class_vars = self.__class__.__dict__
        all_attributes = {**class_vars, **instance_vars}

        filtered_attributes = {k: str(v) for (k, v) in all_attributes.items() if not k[0] == '_'}
        url = self.url.format(**filtered_attributes)
        print(url)
        response = requests.get(url,
                                headers={
                                    'cache-control': "no-cache"
                                })
        self.product_data = response.json()
        print('Raw Data:')
        pprint.pprint(self.product_data)
        return self.product_data

    def post_process(self, data):
        return data

    def execute(self):
        d = self.do_json_request()
        try:
            return self.post_process(d)
        except ProductNotFoundException as err:
            print('product not found')
            raise err
        except Exception as err:
            print('post process error')
            print(err)
            raise err


class Open_Food_Facts(_UPC_lookup):
    url = 'https://world.openfoodfacts.org/api/v0/product/{upc}.json'

    # no access key

    def post_process(self, data):
        if data.get('status', 'success') == 0:
            raise ProductNotFoundException()
        product_data = {
            'title': data['product']['product_name'],
            'description': data['product']['product_name'],
            'upcnumber': self.upc,
            'data_source': self.klass_name
        }
        return product_data


class UPC_Database(_UPC_lookup):
    key = 'UPC_KEY'
    url = 'https://api.upcdatabase.org/product/{upc}/{key}'

    def post_process(self, data):
        if data.get('error', False) == True:
            raise ProductNotFoundException()

        product_data = {
            'title': data['title'],
            'description': data['description'],
            'upcnumber': data['upcnumber'],
            'data_source': self.klass_name,
        }
        return product_data


class EAN_Data(_UPC_lookup):
    url = "https://eandata.com/feed/?v=3&keycode={key}&mode=json&find={upc}&comp=no&get=all"
    key = 'EAN_KEY'

    def post_process(self, data):
        title = data.get('product').get('attributes', {}).get('product', '-')
        if title == '':
            raise ProductNotFoundException()
        product_data = {
            'title': title,
            'description': '',
            'upcnumber': self.upc,
            'data_source': self.klass_name

        }
        return product_data


class EAN_Search(_UPC_lookup):
    url = "https://api.ean-search.org/api?token={key}&op=barcode-lookup&ean={upc}&format=json&lang=1"
    key = 'EAN_SEARCH_KEY'

    def post_process(self, data):
        if "error" in data[0]:
            raise ProductNotFoundException()
        name = data[0]["name"]
        product_data = {
            'title': name,
            'description': name,
            'upcnumber': self.upc,
            'data_source': self.klass_name
        }
        return product_data
