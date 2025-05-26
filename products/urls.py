# products/urls.py

from django.urls import path
from . import views # Assuming views.py is in the same app directory (products/views.py)
from django.conf import settings
from django.conf.urls.static import static

app_name = 'products' # Add an app namespace

urlpatterns = [
    path('', views.product_list, name='product_list'), # Main product listing
    path('home/', views.home, name='home_page'), # Explicit home page (có thể bỏ nếu product_list là trang chủ)
    # path('add/', views.product_add, name='product_add'), # << XÓA NẾU ĐÂY LÀ CỦA ADMIN
    path('edit/<str:pid>/', views.product_edit, name='product_edit'), # << NẾU ĐÂY LÀ VIEW CHỈNH SỬA CỦA ADMIN, NÓ NÊN Ở admin/urls.py
    path('search/', views.product_search, name='product_search_direct'),
    
    path('viewproduct/<str:pid>/', views.product_details, name='product_details'),
    
    path('cart/', views.cart_get, name='cart_get'),
    path('cart/add/<str:pid>/', views.cart_add, name='cart_add'),
    path('cart/delete/<str:pid>/', views.cart_delete, name='cart_delete'),
    
    path('checkout/', views.cart_checkout, name='cart_checkout'),
    
    path('orders/', views.orders_get, name='orders_get'),
    path('orders/details/<int:oid>/', views.order_details, name='order_details'),
    path('orders/cancel/<int:oid>/', views.order_cancel, name='order_cancel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)