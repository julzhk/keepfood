import os

from django.test import TestCase

from barcode_listener.models import generate_signature, DigitEyes_lookup, generate_digiteyes_url, UPC_lookup, EAN_lookup


class TestDigitEyesAPI(TestCase):
    def setUp(self):
        self.ean = '3045320094084'
        self, AUTH_KEY_K = 'sfwefg3v0f8Fo8He4'
        """'This sfwefg3v0f8Fo8He4' is a fake key BTW"""

    def test_digiteyes_signature(self):
        sig = generate_signature(upc='799193996602', auth_key_m=self.AUTH_KEY_K)
        self.assertEqual(sig, '0yJ6PHJU+i0shAfOus/0YWVcEaA=')

    def test_digiteyes_generate_url(self):
        sig = '0yJ6PHJU+i0shAfOus/0YWVcEaA='
        correct = 'https://www.digit-eyes.com/gtin/v2_0/?upcCode=799193996602&language=en&app_key=sfwefg3v0f8Fo8He4&signature=0yJ6PHJU+i0shAfOus/0YWVcEaA='
        url = generate_digiteyes_url(upc='799193996602', sig=sig, auth_key_k=self.AUTH_KEY_K)
        self.assertEqual(correct, url)


class TestREALAPI(TestCase):
    def setUp(self):
        self.ean = '3045320094084'

    def test_upc_lookup(self):
        upc_data = (UPC_lookup(self.ean))
        self.assertEqual(upc_data['newupc'], self.ean)

    def test_ean_lookup(self):
        ean_data = EAN_lookup(self.ean)
        self.assertEqual(ean_data['status']['code'], '200')
        self.assertEqual(ean_data['product']['EAN13'], self.ean)

    def test_digiteyes_url(self):
        self.assertNotEquals(os.environ.get('DIGIT_EYES_KEY_K', '??'), '??')
        ean_data = DigitEyes_lookup(self.ean)
        self.assertEqual(ean_data['return_message'], 'Success')
