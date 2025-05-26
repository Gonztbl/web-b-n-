from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn trang đăng ký
    path('register/', views.register, name='register'),

    # Đường dẫn trang đăng nhập
    path('login/', views.login, name='login'),

    # Đường dẫn trang đăng xuất
    path('logout/', views.logout, name='logout'),
]
