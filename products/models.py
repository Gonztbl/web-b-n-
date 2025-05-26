from django.db import models

class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=10)
    product_name = models.CharField(max_length=25)
    # product_image = models.ImageField(upload_to='products/', blank=True, null=True) # Allow null for now
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    company = models.CharField(max_length=25)
    product_description = models.TextField() # Main description
    quantity_in_stock = models.PositiveIntegerField()
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    # 'description' field seems redundant if product_description is the main one.
    # If kept, ensure its purpose is clear. For now, assume product_description is primary.
    # description = models.TextField(blank=True, null=True) # Short/secondary description

    def __str__(self):
        return f"{self.product_name} ({self.product_id})"

class Cart(models.Model):
    ord = models.AutoField(db_column='ord', primary_key=True) # This seems like an internal PK, not an order number
    quantity = models.PositiveIntegerField(db_column='quantity')
    user = models.CharField(db_column='user', max_length=150) # Match Django's User.username max_length
    # ForeignKey field is 'product', db_column is 'product_id'
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='product_id')

    class Meta:
        db_table = 'cart'
        unique_together = (('user', 'product'),) # Ensures one cart entry per user per product

    def __str__(self):
        return f"Cart: {self.user} - {self.product.product_name} (Qty: {self.quantity})"

class Orders(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'), # Added for consistency with templates
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    ]

    order_id = models.AutoField(db_column='order_id', primary_key=True)
    user = models.CharField(db_column='user', max_length=150) # Match Django's User.username
    customer_name = models.CharField(db_column='customer_name', max_length=100) # Increased length
    address = models.CharField(db_column='address', max_length=255) # Increased length
    phone_number = models.CharField(db_column='phone_number', max_length=20) # Increased length
    total_price = models.DecimalField(db_column='total_price', max_digits=10, decimal_places=2, default=0)
    status = models.CharField(db_column='status', max_length=10, choices=ORDER_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) # Track order creation time

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order {self.order_id} by {self.user} - {self.status}"


class OrderDetails(models.Model):
    # order_id is the ForeignKey field to Orders model
    order_id = models.ForeignKey('Orders', on_delete=models.CASCADE, db_column='order_id_fk') # Renamed db_column to avoid conflict
    # product_id is the ForeignKey field to Product model
    product_id = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, db_column='product_id_fk') # SET_NULL to keep order history if product is deleted
    quantity = models.PositiveIntegerField(db_column='quantity')
    # Removed user field as it's available via order_id.user

    class Meta:
        # unique_together was for ('order_id', 'product_id'), which means order_id (FK to Orders) and product_id (FK to Product)
        unique_together = (('order_id', 'product_id'),) 
        db_table = 'orderdetails'

    def __str__(self):
        product_name = self.product_id.product_name if self.product_id else "N/A"
        return f"OrderDetail: Order {self.order_id.order_id} - Product {product_name} (Qty: {self.quantity})"