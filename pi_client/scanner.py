#!/usr/bin/python
import json
import logging
from random import randint
from time import sleep

import requests
import unicornhat as unicorn

from UHScroll import unicorn_scroll

MAX_CHARS_POST_RESPONSE = 50

UNICORN_HAT_BRIGHT = 255

UNICORN_HAT_FAST_SCROLL = 0.075

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s (%(threadName)-10s) - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("{0}/{1}.log".format('logs', 'scanner')),
        logging.StreamHandler()
    ])

# KEEPFOOD_KEY = os.environ.get('KEEPFOOD_KEY', '??')
# KEEPFOOD_URL = os.environ.get('KEEPFOOD_URL', '??')

# something like KEEPFOOD_URL=https://<URL>/api/product/%s/scan/
KEEPFOOD_URL = 'https://keepfood.pagekite.me/api/product/%s/scan/'
KEEPFOOD_KEY = '9268ae6c5f37d4e7bd67ab0685478737d7b9e9f7'
logging.info('start with ' + KEEPFOOD_URL)
UPC_LOOKUP_ERROR = 'upc number error'

"""
Run this on the raspberry pi with the USB barcode scanner attached
It needs an environment variable of the UPC database acccess key set

Unicorn hat used for scanning confirmation: Twinkles!

USAGE: 
add UPC_KEY as env variable: 
 * sudo nano /etc/profile add at end:
    export UPC_KEY=<YOUR KEY HERE, no quotes>

open new shell and execute with:
 * sudo -E python3 scanner.py
 * (-E means preserve env variables)

Inspired by https://www.piddlerintheroot.com/barcode-scanner/

# https://www.raspberrypi.org/forums/viewtopic.php?f=45&t=55100
Barcode code obtained from 'brechmos'

"""
CHARMAP_LOWERCASE = {4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k',
                     15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v',
                     26: 'w', 27: 'x', 28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7',
                     37: '8', 38: '9', 39: '0', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';',
                     52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'}
CHARMAP_UPPERCASE = {4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K',
                     15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V',
                     26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&',
                     37: '*', 38: '(', 39: ')', 44: ' ', 45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':', 52: '"',
                     53: '~', 54: '<', 55: '>', 56: '?'}
CR_CHAR = 40
SHIFT_CHAR = 2

assert (KEEPFOOD_URL != '??'), 'KEEPFOOD_URL Env vars not set? or start with sudo -E scanner.py'
assert (KEEPFOOD_KEY != '??'), 'KEEPFOOD_KEY Env vars not set? or start with sudo -E scanner.py'

def barcode_reader():
    barcode_string_output = ''
    # barcode can have a 'shift' character; this switches the character set
    # from the lower to upper case variant for the next character only.
    CHARMAP = CHARMAP_LOWERCASE

    with open('/dev/hidraw0', 'rb') as fp:
        while True:
            # step through returned character codes, ignore zeroes
            for char_code in [element for element in fp.read(8) if element > 0]:
                if char_code == CR_CHAR:
                    # all barcodes end with a carriage return
                    return barcode_string_output
                if char_code == SHIFT_CHAR:
                    # use uppercase character set next time
                    CHARMAP = CHARMAP_UPPERCASE
                else:
                    # if the charcode isn't recognized, add ?
                    barcode_string_output += CHARMAP.get(char_code, '?')
                    # reset to lowercase character map
                    CHARMAP = CHARMAP_LOWERCASE


def post_data_to_server(upcnumber):
    logging.debug('post data to serverexit')
    post_url = KEEPFOOD_URL % upcnumber
    logging.debug('post to ' + post_url)
    response = requests.post(
        post_url,
        data=json.dumps({'upcnumber': upcnumber}),
        headers={
            'content-type': 'application/json',
            'Authorization': 'Token %s' % KEEPFOOD_KEY
        }
    )
    status_code = response.status_code
    logging.debug('response code ' + str(status_code))
    if status_code == 200:
        show_twinkle_confirmation(32, 255, 32)
    else:
        unicorn_message(str(status_code))
        show_colour_confirmation(255, 32, 32)
    return response.content.decode('utf-8')[:MAX_CHARS_POST_RESPONSE]


def show_colour_confirmation(r=160, g=64, b=128):
    width, height = unicorn.get_shape()
    for i in range(0, width * height):
        x = i % width
        y = i // height
        unicorn.set_pixel(x, y, r, g, b)
        unicorn.show()
        sleep(0.01)
    unicorn.off()


def show_twinkle_confirmation(rx=255, gx=255, bx=255):
    width, height = unicorn.get_shape()
    for i in range(0, 300):
        x = randint(0, (width - 1))
        y = randint(0, (height - 1))
        r = randint(0, rx)
        g = randint(0, gx)
        b = randint(0, bx)
        unicorn.set_pixel(x, y, r, g, b)
        unicorn.show()
    unicorn.off()


def unicorn_message(content, colour='red'):
    logging.info(content)
    unicorn_scroll(str(content),
                   colour,
                   UNICORN_HAT_BRIGHT,
                   UNICORN_HAT_FAST_SCROLL
                   )


def unicorn_init():
    unicorn.set_layout(unicorn.AUTO)
    unicorn.rotation(0)
    unicorn.brightness(0.5)


if __name__ == '__main__':
    unicorn_init()
    unicorn_message('Ready!', 'blue')
    try:
        while True:
            upcnumber = barcode_reader()
            logging.info('scanned: ' + str(upcnumber))
            post_data_to_server(upcnumber)
    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt')
        unicorn_message('bye')
        show_colour_confirmation(32, 32, 255)
    except Exception as err:
        logging.error(err)
        show_colour_confirmation(32, 32, 255)
