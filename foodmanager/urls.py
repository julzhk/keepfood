
from django.contrib import admin
from django.urls import path
from barcode_listener.views import listener
urlpatterns = [
    path('', listener, name='listener'),
    path('admin/', admin.site.urls),
]
