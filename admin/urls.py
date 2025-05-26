from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn để thêm sản phẩm mới
    path('products/add/', views.product_add, name='product_add'),
    
    # Đường dẫn để xác nhận việc thêm sản phẩm mới
    path('products/accept_add/', views.product_accept_add, name='product_accept_add'),

    # Đừng thay đổi những đường dẫn dưới đây
    path('products/<str:pid>/', views.product_change, name='product_change'),
    path('products/accept_change/<str:pid>', views.product_accept_change, name='product_accept_change'),
    path('products/delete/<str:pid>', views.product_delete, name='product_delete'),
    
# Đường dẫn để thay đổi trạng thái đơn hàng
    path('orders/change_status/<str:oid>/<str:action>/', views.order_status_change, name='order_status_change'),
    
    # Đường dẫn để xem chi tiết đơn hàng
    path('orders/details/<str:oid>', views.order_details, name='order_details'),
    
    # Đường dẫn để lọc đơn hàng theo trạng thái
    path('orders/filter/', views.order_filter, name='order_filter'),
]

