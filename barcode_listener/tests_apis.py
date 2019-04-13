import os

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from barcode_listener.models import generate_signature, DigitEyes_lookup, generate_digiteyes_url, UPC_lookup, EAN_lookup
from .models import Product, Stock


class TestDigitEyesAPI(TestCase):
    def setUp(self):
        self.ean = '3045320094084'
        self.AUTH_KEY_K = 'sfwefg3v0f8Fo8He4'
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
        self.assertEqual(upc_data['upcnumber'], self.ean)

    def test_ean_lookup(self):
        ean_data = EAN_lookup(self.ean)
        self.assertEqual(ean_data['status']['code'], '200')
        self.assertEqual(ean_data['product']['EAN13'], self.ean)

    def test_digiteyes_url(self):
        self.assertNotEquals(os.environ.get('DIGIT_EYES_KEY_K', '??'), '??')
        ean_data = DigitEyes_lookup(self.ean)
        self.assertEqual(ean_data['return_message'], 'Success')


class TestRealAPI(TestCase):
    def setUp(self):
        self.adminuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.adminuser.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.adminuser)

    def test_pasta(self):
        upc = '8000139910753'
        response = self.client.post(f'/api/product/{upc}/scan/', follow=True)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Stock.objects.count(), 1)
        self.assertEqual(response.status_code, 200)
