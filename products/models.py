# products/models.py
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=10, verbose_name="Mã sản phẩm")
    product_name = models.CharField(max_length=25, verbose_name="Tên sản phẩm")
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Ảnh sản phẩm")
    company = models.CharField(max_length=25, verbose_name="Nhà sản xuất")
    product_description = models.TextField(verbose_name="Mô tả sản phẩm")
    quantity_in_stock = models.PositiveIntegerField(verbose_name="Số lượng tồn kho")
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá bán")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Các sản phẩm"

    def __str__(self):
        return f"{self.product_name} ({self.product_id})"

class Cart(models.Model):
    ord = models.AutoField(db_column='ord', primary_key=True)
    quantity = models.PositiveIntegerField(db_column='quantity', verbose_name="Số lượng")
    user = models.CharField(db_column='user', max_length=150) # Tạm giữ để tương thích
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='product_id', verbose_name="Sản phẩm")

    class Meta:
        db_table = 'cart'
        unique_together = (('user', 'product'),)
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Các giỏ hàng"

    def __str__(self):
        return f"Giỏ hàng: {self.user} - {self.product.product_name} (Số lượng: {self.quantity})"

class Orders(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Đang chờ xử lý'),
        ('PendPay', 'Chờ thanh toán'),
        ('Confirmed', 'Đã xác nhận'),
        ('Processing', 'Đang xử lý'),
        ('Shipped', 'Đã gửi hàng'),
        ('Delivered', 'Đã giao hàng'),
        ('Canceled', 'Đã hủy'),
        ('PayError', 'Lỗi thanh toán'),
        ('StockErr', 'Hết hàng (cần hoàn tiền)'), # Làm rõ hơn
        ('PayExp', 'Thanh toán hết hạn'),
        ('Failed', 'Thất bại'),
    ]

    order_id = models.AutoField(db_column='order_id', primary_key=True)
    payment_order_code = models.BigIntegerField(
    unique=True,
    db_index=True,
    null=True, # Cho phép null để các đơn hàng cũ không bị lỗi
    blank=True,
    verbose_name="Mã đơn hàng PayOS"
    )
    user = models.CharField(db_column='user', max_length=150, verbose_name="Tên người dùng")
    customer_name = models.CharField(db_column='customer_name', max_length=100, verbose_name="Tên khách hàng")
    address = models.CharField(db_column='address', max_length=255, verbose_name="Địa chỉ")
    phone_number = models.CharField(db_column='phone_number', max_length=20, verbose_name="Số điện thoại")
    total_price = models.DecimalField(db_column='total_price', max_digits=10, decimal_places=2, default=0, verbose_name="Tổng tiền")
    status = models.CharField(db_column='status', max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending', verbose_name="Trạng thái") # SỬA Ở ĐÂY
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Ngày tạo")
    
    # THÊM CÁC TRƯỜNG MỚI
    payment_link = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link thanh toán")
    payment_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mã giao dịch PayOS")

    class Meta:
        db_table = 'orders'
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Các đơn hàng"

    def __str__(self):
        return f"Đơn hàng #{self.order_id} của {self.user} - {self.get_status_display()}"


class OrderDetails(models.Model):
    # SỬA Ở ĐÂY: Đổi tên trường
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, db_column='order_id_fk', verbose_name="Đơn hàng")
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, db_column='product_id_fk', verbose_name="Sản phẩm")
    quantity = models.PositiveIntegerField(db_column='quantity', verbose_name="Số lượng")
    
    class Meta:
        # SỬA Ở ĐÂY: Cập nhật unique_together
        unique_together = (('order', 'product'),) 
        db_table = 'orderdetails'
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Các chi tiết đơn hàng"

    def __str__(self):
        # SỬA Ở ĐÂY: Dùng tên trường mới
        product_name = self.product.product_name if self.product else "Sản phẩm đã xóa"
        return f"Chi tiết ĐH #{self.order.order_id} - {product_name} (Số lượng: {self.quantity})"

class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Rất tệ'),
        (2, '2 - Tệ'),
        (3, '3 - Bình thường'),
        (4, '4 - Tốt'),
        (5, '5 - Rất tốt'),
    ]

    # SỬA Ở ĐÂY: Đổi tên trường để dễ hiểu hơn
    order_detail = models.OneToOneField(
        OrderDetails,
        on_delete=models.CASCADE,
        related_name='review',
        help_text="Mục cụ thể trong đơn hàng đang được đánh giá.",
        verbose_name="Chi tiết đơn hàng"
    )

    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Xếp hạng")
    comment = models.TextField(blank=True, null=True, verbose_name="Bình luận")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        db_table = 'product_reviews'
        ordering = ['-created_at']
        verbose_name = "Đánh giá sản phẩm"
        verbose_name_plural = "Các đánh giá sản phẩm"

    def __str__(self):
        product_name = "Không xác định"
        user_name = "Không xác định"
        order_id_val = "Không xác định"

        if self.order_detail:
            if self.order_detail.product:
                product_name = self.order_detail.product.product_name
            if self.order_detail.order:
                user_name = self.order_detail.order.user
                order_id_val = self.order_detail.order.order_id
        
        return f"Đánh giá cho '{product_name}' trong ĐH #{order_id_val} bởi {user_name}"

    @property
    def user_display_name(self):
        if self.order_detail and self.order_detail.order:
            username = self.order_detail.order.user
            if len(username) > 3:
                 return f"{username[:3]}***"
            return username
        return "Ẩn danh"