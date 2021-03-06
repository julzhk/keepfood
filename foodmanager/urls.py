from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views as rest_framework_auth_views

from barcode_listener import views
from barcode_listener import views as barcode_views

router = routers.DefaultRouter()
router.register(r'product', views.ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^get_auth_token/$', rest_framework_auth_views.obtain_auth_token, name='get_auth_token'),

    path('admin/', admin.site.urls),
    path('tags', barcode_views.tag_list, name='tag_list'),
    path('old', barcode_views.old_stock_report, name='old_stock'),
    path('new', barcode_views.new_stock_report, name='new_stock'),
    path('empty', barcode_views.empty_stock_report, name='empty_stock'),
    path('', barcode_views.stock_report, name='home'),
]

# when POST’ing to http://<YOUR SITE>/get_auth_token/ with the following data
# (assuming this username / password exists):
# { 'username': 'admin', 'password': 'admin' }
# you’ll receive something that looks like the following:
# { 'token': '93138ba960dfb4ef2eef6b907718ae04400f606a' }
