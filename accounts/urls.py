from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn trang đăng ký
    path('register/', views.register, name='register'),

    # Đường dẫn trang đăng nhập
    path('login/', views.login, name='login'),

    # Đường dẫn trang đăng xuất
    path('logout/', views.logout, name='logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
