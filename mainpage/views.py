from django.shortcuts import render
# QUAN TRỌNG: Import model Product và OrderDetails từ app 'products'
from products.models import Product, OrderDetails
from django.db.models import Sum, Value, IntegerField
from django.db.models.functions import Coalesce
import logging

logger = logging.getLogger(__name__)

def home(request): # Hoặc tên view của bạn (ví dụ: index_view)
    logger.info("--- Trang chủ (mainpage.views.home) được gọi ---")

    # Logic lấy 3 sản phẩm bán chạy nhất còn hàng (COPY TỪ products.views.home)
    products_with_sales = Product.objects.filter(
        quantity_in_stock__gt=0
    ).annotate(
        total_sold_quantity=Coalesce(Sum('orderdetails__quantity'), Value(0), output_field=IntegerField())
    )
    featured_products_query = products_with_sales.order_by('-total_sold_quantity', '-product_id')[:3]

    logger.info(f"Số lượng sản phẩm nổi bật (bán chạy) tìm thấy: {featured_products_query.count()}")
    # ... (thêm log chi tiết sản phẩm nếu muốn) ...

    context = {
        'featured_products': featured_products_query,
        # Các biến context khác mà view này có thể đã có
    }
    return render(request, 'index.html', context) # Đảm bảo render đúng template 'index.html'