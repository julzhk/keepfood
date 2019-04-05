from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Product


class TestAPI(TestCase):

    def test_simple(self):
        self.adminuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.adminuser.save()
        client = APIClient()
        client.force_authenticate(user=self.adminuser)
        response = client.post('/api/product/', data={'upcnumber': '3045320094084'}, follow=True)
        print(response.content)
        print(response.status_code)
        print()
        print(Product.objects.all())
