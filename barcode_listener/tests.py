from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Product, Stock


class TestAPI(TestCase):

    def setUp(self):
        self.adminuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.adminuser.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.adminuser)

    def test_scan_creates_product_and_two_stock_items(self):
        client = self.client
        response = client.post('/api/product/', data={'upcnumber': '3045320094084'}, follow=True)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Stock.objects.count(), 1)

        response = client.post('/api/product/', data={'upcnumber': '3045320094084'}, follow=True)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Stock.objects.count(), 2)
