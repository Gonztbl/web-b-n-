from django.urls import path, include
from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn trang chủ
    path('', views.home, name='home'),

    # Đường dẫn cho các sản phẩm (đưa tới các URL của ứng dụng products)
    path('products/', include('products.urls')),
]
