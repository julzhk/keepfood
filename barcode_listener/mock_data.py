def mock_UPC_feed(upc='3045320094084'):
    return {'age': '',
            'alias': '',
            'brand': '',
            'category': '',
            'color': '',
            'description': '',
            'error': False,
            'gender': '',
            'msrp': '0.00',
            'newupc': '3045320094084',
            'rate/down': '0',
            'rate/up': '0',
            'size': '',
            'st0s': '3045320094084',
            'status': 200,
            'title': 'Bonne Maman Rasberry Conserve',
            'type': '',
            'unit': '',
            'upcnumber': '3045320094084'}


def mock_EAN_feed(upc='3045320094084'):
    return {'company': {'address': '',
                        'locked': '0',
                        'logo': '',
                        'name': 'Andros France Snc',
                        'phone': '',
                        'url': ''},
            'product': {'EAN13': '3045320094084',
                        'attributes': {'asin_com': 'B003CBO23K',
                                       'binding': 'Grocery',
                                       'category': '51',
                                       'category_text': 'Food',
                                       'category_text_long': 'Food',
                                       'description': '370G',
                                       'height': '3.8200',
                                       'height_extra': 'in',
                                       'height_extra_id': '501',
                                       'height_extra_long': 'inches',
                                       'language': '553',
                                       'language_text': 'en',
                                       'language_text_long': 'English',
                                       'length': '3.3500',
                                       'length_extra': 'in',
                                       'length_extra_id': '501',
                                       'length_extra_long': 'inches',
                                       'long_desc': '*** only visible with paid data feed '
                                                    '***',
                                       'model': '100103218',
                                       'price_new': '2.7300',
                                       'price_new_extra': 'USD',
                                       'price_new_extra_id': '537',
                                       'price_new_extra_long': 'US Dollars',
                                       'product': 'Bonne Maman - Raspberry Conserve - '
                                                  '370g',
                                       'weight': '13.1200',
                                       'weight_extra': 'oz',
                                       'weight_extra_id': '513',
                                       'weight_extra_long': 'ounces',
                                       'width': '3.3500',
                                       'width_extra': 'in',
                                       'width_extra_id': '501',
                                       'width_extra_long': 'inches'},
                        'barcode': {'EAN13': 'https://eandata.com/image/3045320094084.png'},
                        'image': 'https://eandata.com/image/products/304/532/009/3045320094084.jpg',
                        'locked': '0',
                        'modified': '2017-05-22 05:51:29'},
            'status': {'code': '200',
                       'find': '3045320094084',
                       'message': 'free 7/15',
                       'run': '0.0919',
                       'runtime': '0.0994',
                       'search': 'normal',
                       'version': '3.1'}}


def mock_UPC_data(upc=None):
    return {'upcnumber': '3045320094084', 'title': 'Bonne Maman Rasberry Conserve', 'description': ''}