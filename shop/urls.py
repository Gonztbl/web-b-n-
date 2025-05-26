from django.contrib import admin
from django.urls import path, include
# Thêm 2 dòng sau:
from django.conf import settings
from django.conf.urls.static import static  # ✅

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainpage.urls')),
    path('products/', include('products.urls')),
    path('admin/', include('admin.urls')),
    path('accounts/', include('accounts.urls')),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # ✅