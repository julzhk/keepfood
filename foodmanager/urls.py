
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from barcode_listener.views import listener
from django.urls import include, path
from rest_framework import routers
from barcode_listener import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('boom', listener, name='listener'),
    path('admin/', admin.site.urls),
]
