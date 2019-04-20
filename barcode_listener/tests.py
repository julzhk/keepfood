from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from taggit.models import Tag

from .models import Product, Stock, Log


class TestAPI(TestCase):

    def setUp(self):
        self.adminuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.adminuser.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.adminuser)

    def test_scan_creates_one_product_and_two_stock_items(self):
        response = self.client.post('/api/product/3045320094084/scan/', follow=True)
        self.assertEqual(Product.objects.count(), 1)
        first_product = Product.objects.first()
        self.assertTrue('MOCK' in first_product.title, first_product.title)
        self.assertEqual(Stock.objects.count(), 1)

        response = self.client.post('/api/product/3045320094084/scan/', follow=True)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Stock.objects.count(), 2)

    def test_new_product_scan_with_control_code_scan(self):
        """
        Scan a control char then a new product
        """
        IS_A_CAN_UPC_CODE = '000001'
        # create the control code first:
        is_can_tag = Tag(name='is_can', slug=IS_A_CAN_UPC_CODE).save()
        self.assertEqual(Tag.objects.count(), 1)

        response = self.client.post('/api/product/%s/scan/' % IS_A_CAN_UPC_CODE, follow=True)
        self.assertEqual(Log.objects.count(), 1)
        response = self.client.post('/api/product/3045320094084/scan/', follow=True)
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Stock.objects.count(), 1)
        product_tags = Product.objects.first().tags.all()
        # product tags removed
        self.assertEqual(product_tags.count(), 0)
        stock_tags = Stock.objects.first().tags.all()
        self.assertEqual(stock_tags.count(), 1)

    def test_existing_product_scan_with_two_control_code_scans(self):
        """
        Scan a control char then a product
        """
        IS_A_CAN_UPC_CODE = '000001'
        SIX_MONTH_LIFE = '000002'
        data = mock_UPC_data()
        p = Product(**data)
        p.save()
        Tag(name='is_can', slug=IS_A_CAN_UPC_CODE).save()
        Tag(name='six_months_life', slug=SIX_MONTH_LIFE).save()
        self.assertEqual(Tag.objects.count(), 2)

        self.client.post('/api/product/%s/scan/' % IS_A_CAN_UPC_CODE, follow=True)
        self.client.post('/api/product/%s/scan/' % SIX_MONTH_LIFE, follow=True)
        self.assertEqual(Log.objects.count(), 2)

        response = self.client.post('/api/product/3045320094084/scan/', follow=True)
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Stock.objects.count(), 1)
        product_tags = Product.objects.first().tags.all()
        # product tags are not supported now
        self.assertEqual(product_tags.count(), 0)
        stock_tags = Stock.objects.first().tags.all()
        self.assertEqual(stock_tags.count(), 2)


class TestControlCharacters(TestCase):
    def setUp(self):
        self.adminuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.adminuser.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.adminuser)
        self.IS_A_CAN_UPC_CODE = '000001'
        self.SIX_MONTH_LIFE = '000002'
        from .views import RESET_STACK_TAG_NAME, DELETE_TAG_NAME
        is_can_tag = Tag(name='is_can', slug=self.IS_A_CAN_UPC_CODE).save()
        six_month_tag = Tag(name='six_months_life', slug=self.SIX_MONTH_LIFE).save()
        self.reset_stack_tag = Tag(name=RESET_STACK_TAG_NAME, slug='000003')
        self.reset_stack_tag.save()
        self.delete_stock_tag = Tag(name=DELETE_TAG_NAME, slug='000004')
        self.delete_stock_tag.save()
        self.assertEqual(Tag.objects.count(), 4)

    def test_assign_shelf_life(self):
        response = self.client.post('/api/product/%s/scan/' % self.SIX_MONTH_LIFE, follow=True)
        response = self.client.post('/api/product/3045320094084/scan/', follow=True)
        stock = Stock.objects.first()
        date_use_by = timezone.now() + timedelta(days=30 * 6) - timedelta(days=1)
        self.assertTrue(stock.date_use_by > date_use_by)

    def test_reset_stack(self):
        response = self.client.post('/api/product/%s/scan/' % self.SIX_MONTH_LIFE, follow=True)
        response = self.client.post('/api/product/%s/scan/' % self.IS_A_CAN_UPC_CODE, follow=True)
        self.assertEqual(Log.objects.count(), 2)
        response = self.client.post('/api/product/%s/scan/' % self.reset_stack_tag.slug, follow=True)
        self.assertEqual(Stock.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)

    def test_delete_stock(self):
        response = self.client.post('/api/product/%s/scan/' % self.delete_stock_tag.slug, follow=True)
        response = self.client.post('/api/product/3045320094084/scan/', follow=True)
        self.assertEqual(Stock.objects.count(), 0)
