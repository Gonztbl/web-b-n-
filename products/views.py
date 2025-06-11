# products/views.py
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q, Avg
from django.utils.html import escape
from django.shortcuts import render, redirect, get_object_or_404
import logging
from django.urls import reverse
from .models import Product, Cart, Orders, OrderDetails, ProductReview
from .forms import ProductForm, ProductReviewForm
from django.core.paginator import Paginator
import os
import requests # Không cần thiết nếu chỉ dùng PayOS SDK
import json # Để logging nếu cần
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import time
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from payos import PayOS
from payos.type import PaymentData, ItemData
from payos.custom_error import PayOSError

logger = logging.getLogger(__name__)

payos_client = None
if settings.PAYOS_CLIENT_ID and settings.PAYOS_API_KEY and settings.PAYOS_CHECKSUM_KEY:
    try:
        payos_client = PayOS(
            client_id=settings.PAYOS_CLIENT_ID,
            api_key=settings.PAYOS_API_KEY,
            checksum_key=settings.PAYOS_CHECKSUM_KEY
        )
        logger.info("PayOS client initialized successfully.")
    except TypeError as te:
        logger.error(f"Failed to initialize PayOS client due to TypeError: {te}. Check credential types.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during PayOS client initialization: {e}")
else:
    logger.warning("PAYOS_CLIENT_ID, PAYOS_API_KEY, or PAYOS_CHECKSUM_KEY not found in settings. Payment via PayOS will not be available.")
    if not settings.PAYOS_CLIENT_ID: logger.warning("PAYOS_CLIENT_ID is missing.")
    if not settings.PAYOS_API_KEY: logger.warning("PAYOS_API_KEY is missing.")
    if not settings.PAYOS_CHECKSUM_KEY: logger.warning("PAYOS_CHECKSUM_KEY is missing.")


# --- Các view khác giữ nguyên ---
# ... (product_edit, product_add, home, product_list, product_search, product_details, cart_add, cart_get, orders_get) ...
def product_edit(request, pid):
    product = get_object_or_404(Product, product_id=pid)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product, is_edit=True)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product, is_edit=True)
    return render(request, 'products/product_add.html', {'form': form, 'product': product, 'url': request.path, 'is_edit': True})

def product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('products:product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_add.html', {'form': form, 'product': None, 'url': request.path, 'is_edit': False})

def home(request):
    return render(request, 'index.html')

def product_list(request):
    pds_query = Product.objects.all()
    pname_q = request.GET.get("pname", "").strip()
    filter_q = request.GET.get("filter", "").strip()
    sort_q = request.GET.get("sort", "").strip()

    if pname_q: pds_query = pds_query.filter(product_name__icontains=pname_q)
    if filter_q == 'avail': pds_query = pds_query.filter(quantity_in_stock__gt=0)
    elif filter_q == 'sold-out': pds_query = pds_query.filter(quantity_in_stock=0)

    if sort_q == 'name-a-to-z': pds_query = pds_query.order_by('product_name')
    elif sort_q == 'name-z-to-a': pds_query = pds_query.order_by('-product_name')
    elif sort_q == 'price-up': pds_query = pds_query.order_by('sell_price')
    elif sort_q == 'price-down': pds_query = pds_query.order_by('-sell_price')
    else: pds_query = pds_query.order_by('product_id')

    paginator = Paginator(pds_query, 16) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'products': page_obj, 'count': pds_query.count(), 'query_pname': pname_q, 'query_filter': filter_q, 'query_sort': sort_q}
    return render(request, 'products/product.html', context)

def product_search(request):
    query_params = request.GET.copy()
    if not query_params: return redirect('products:product_list')
    list_url = reverse('products:product_list')
    return redirect(f"{list_url}?{query_params.urlencode()}")

def product_details(request, pid):
    product = get_object_or_404(Product, product_id=pid)
    display_quantity_in_cart = 0
    if request.user.is_authenticated and not request.user.is_superuser:
        try:
            cart_item = Cart.objects.get(user=request.user.username, product=product)
            display_quantity_in_cart = cart_item.quantity
        except Cart.DoesNotExist: display_quantity_in_cart = 0
    # Dòng đã sửa, rõ ràng hơn
    reviews = ProductReview.objects.filter(order_detail__product=product).select_related('order_detail__order').order_by('-created_at')
    average_rating_data = reviews.aggregate(Avg('rating'))
    average_rating = average_rating_data['rating__avg']
    review_count = reviews.count()
    context = {'product': product, 'quantity': display_quantity_in_cart, 'reviews': reviews, 'average_rating': average_rating, 'review_count': review_count, 'rating_choices_range': range(1, 6), 'RATING_CHOICES_MAP': dict(ProductReview.RATING_CHOICES)}
    return render(request, 'products/product_details.html', context)

def cart_add(request, pid):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to add items to your cart.")
        return redirect('login') 
    if request.user.is_superuser:
        messages.error(request, "Admin users cannot add items to the cart.")
        return redirect('products:product_list') 
    storage = messages.get_messages(request); storage.used = True 
    product_instance = get_object_or_404(Product, product_id=pid)
    if request.method == 'POST':
        quantity_str = request.POST.get('quantity', '').strip()
        if not quantity_str.isdigit() or int(quantity_str) < 0:
            messages.error(request, 'Invalid quantity specified!')
            return redirect('products:product_details', pid=pid) 
        quantity_desired = int(quantity_str) 
    else:
        messages.error(request, "Invalid request to add to cart.")
        return redirect('products:product_details', pid=pid) 
    user_username = request.user.username
    if quantity_desired == 0:
        deleted_count, _ = Cart.objects.filter(user=user_username, product=product_instance).delete()
        if deleted_count > 0: messages.info(request, f'{product_instance.product_name} has been removed from your cart.')
        return redirect('products:product_details', pid=pid) 
    cart_item, created = Cart.objects.get_or_create(user=user_username, product=product_instance, defaults={'quantity': 0})
    if quantity_desired > product_instance.quantity_in_stock:
        messages.warning(request, f"Sorry, we only have {product_instance.quantity_in_stock} of {product_instance.product_name} in stock.")
        if product_instance.quantity_in_stock > 0 :
            if cart_item.quantity != product_instance.quantity_in_stock: 
                cart_item.quantity = product_instance.quantity_in_stock; cart_item.save()
                messages.info(request, f"Quantity for {product_instance.product_name} set to max available: {product_instance.quantity_in_stock}.")
        elif cart_item.pk: 
             cart_item.delete(); messages.info(request, f"{product_instance.product_name} is out of stock and removed from cart.")
    else:
        if cart_item.quantity != quantity_desired: 
            cart_item.quantity = quantity_desired; cart_item.save()
            if created and quantity_desired > 0: messages.success(request, f'Added {quantity_desired} of {product_instance.product_name} to cart!')
            elif not created and quantity_desired > 0: messages.success(request, f'Updated {product_instance.product_name} in cart to {quantity_desired}.')
    return redirect('products:product_details', pid=pid) 

def cart_get(request):
    if not request.user.is_authenticated: return redirect('login') 
    if request.user.is_superuser:
        messages.error(request, "Admin users do not have a cart."); return redirect('products:product_list')
    user_cart_items_query = Cart.objects.filter(user=request.user.username).select_related('product')
    processed_cart_items_list = []; stock_changed_flag = False 
    for item in user_cart_items_query:
        product_object = item.product if hasattr(item, 'product') and isinstance(item.product, Product) else None
        if not product_object:
            try: product_object = Product.objects.get(product_id=item.product_id)
            except Product.DoesNotExist:
                messages.error(request, f"Product ID '{item.product_id}' (no longer exists) removed from cart."); item.delete(); stock_changed_flag = True; continue
        if product_object.quantity_in_stock == 0:
            messages.warning(request, f"{product_object.product_name} removed (out of stock)."); item.delete(); stock_changed_flag = True
        elif item.quantity > product_object.quantity_in_stock:
            messages.info(request, f"Quantity of {product_object.product_name} adjusted to {product_object.quantity_in_stock} (stock change).")
            item.quantity = product_object.quantity_in_stock; item.save(update_fields=['quantity']); processed_cart_items_list.append({'cart_item_obj': item, 'product_obj': product_object, 'quantity': item.quantity}); stock_changed_flag = True
        else: processed_cart_items_list.append({'cart_item_obj': item, 'product_obj': product_object, 'quantity': item.quantity})
    current_total_price = sum(entry['product_obj'].sell_price * entry['quantity'] for entry in processed_cart_items_list)
    return render(request, 'cart.html', {'cart_entries': processed_cart_items_list, 'changed': stock_changed_flag, 'total': current_total_price})

def orders_get(request):
    if not request.user.is_authenticated: return redirect('login') 
    orders_list_query = Orders.objects.all() if request.user.is_superuser else Orders.objects.filter(user=request.user.username)
    status_filter_from_url = request.GET.get('status', '').strip()
    if status_filter_from_url:
        model_status_filter = next((val for val, _ in Orders.ORDER_STATUS_CHOICES if status_filter_from_url == val.lower()), None)
        if model_status_filter: orders_list_query = orders_list_query.filter(status=model_status_filter)
    orders_list_query = orders_list_query.order_by('-order_id')
    return render(request, 'order.html', {'orders': orders_list_query, 'user_order_status_choices': Orders.ORDER_STATUS_CHOICES})


# products/views.py

def cart_checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        messages.error(request, "Admin users cannot checkout.")
        return redirect('products:product_list')

    storage = messages.get_messages(request)
    storage.used = True

    user_cart_items_query = Cart.objects.filter(user=request.user.username).select_related('product')
    valid_items_for_checkout = []
    checkout_total_price = 0
    cart_issues_found = False

    for item in user_cart_items_query:
        product_object = item.product
        if not product_object:
            messages.error(request, f"Một sản phẩm không còn tồn tại đã bị xóa khỏi giỏ hàng.")
            item.delete(); cart_issues_found = True; continue
        
        if product_object.quantity_in_stock == 0:
            messages.warning(request, f"'{product_object.product_name}' hết hàng, đã xóa khỏi giỏ.")
            item.delete(); cart_issues_found = True; continue
        elif item.quantity > product_object.quantity_in_stock:
            messages.info(request, f"Số lượng '{product_object.product_name}' giảm còn {product_object.quantity_in_stock} (tối đa).")
            item.quantity = product_object.quantity_in_stock
            item.save(update_fields=['quantity'])
        
        valid_items_for_checkout.append({'cart_item': item, 'product_obj': product_object, 'quantity': item.quantity})
        checkout_total_price += product_object.sell_price * item.quantity

    if cart_issues_found and not valid_items_for_checkout:
        messages.info(request, "Giỏ hàng trống sau khi kiểm tra kho.")
        return redirect('products:product_list')
    elif cart_issues_found:
         messages.warning(request, "Một vài sản phẩm đã được điều chỉnh/xóa. Vui lòng kiểm tra lại.")
    
    if not valid_items_for_checkout:
        messages.info(request, "Giỏ hàng trống. Vui lòng thêm sản phẩm.")
        return redirect('products:product_list')

    if request.method == 'POST':
        name = escape(request.POST.get('name', '')).strip()
        address = escape(request.POST.get('address', '')).strip()
        phone = escape(request.POST.get('phone', '')).strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if not all([name, address, phone]):
            messages.error(request, "Vui lòng điền đầy đủ Tên, Địa chỉ, SĐT.")
            return render(request, 'checkout.html', {'checkout_items': valid_items_for_checkout, 'total': checkout_total_price, 'form_data': request.POST})

        initial_order_status = 'PendPay' if payment_method == 'vietqr_payos' else 'Pending'
        
        order = None
        # Bọc các thao tác với database trong một transaction để đảm bảo toàn vẹn
        with transaction.atomic():
            order = Orders(
                user=request.user.username, 
                customer_name=name, 
                address=address, 
                phone_number=phone, 
                total_price=checkout_total_price, 
                status=initial_order_status
            )
            order.save()

            for entry in valid_items_for_checkout:
                OrderDetails.objects.create(
                    order=order, # Dùng instance `order`
                    product=entry['product_obj'], # Dùng instance `product`
                    quantity=entry['quantity']
                )

        if payment_method == 'vietqr_payos':
            if not payos_client:
                messages.error(request, "Dịch vụ PayOS không khả dụng. Chọn phương thức khác.")
                order.status = "Failed"; order.save(update_fields=['status'])
                return render(request, 'checkout.html', {'checkout_items': valid_items_for_checkout, 'total': checkout_total_price, 'form_data': request.POST})
            
            try:
                # TẠO MÃ GIAO DỊCH DUY NHẤT VÀ LƯU LẠI
                # Dùng timestamp (ms) kết hợp với order_id để đảm bảo 100% không trùng
                order_code_for_gateway = int(time.time() * 1000) + order.order_id
                order.payment_order_code = order_code_for_gateway
                order.save(update_fields=['payment_order_code'])

                amount_in_vnd_int = int(round(checkout_total_price))
                description_text = f"Thanh toan don hang DH{order.order_id}"

                payment_data_obj = PaymentData(
                    orderCode=order_code_for_gateway, # SỬ DỤNG MÃ MỚI
                    amount=amount_in_vnd_int,
                    description=description_text,
                    cancelUrl=request.build_absolute_uri(reverse('products:payment_cancel')),
                    returnUrl=request.build_absolute_uri(reverse('products:payment_return')),
                    buyerName=name,
                    buyerPhone=phone,
                )
                
                create_payment_result_obj = payos_client.createPaymentLink(payment_data_obj)
                
                if create_payment_result_obj and create_payment_result_obj.checkoutUrl:
                    logger.info(f"PayOS payment link created for order {order.order_id}. URL: {create_payment_result_obj.checkoutUrl}")
                    # Lưu link thanh toán để có thể truy xuất sau này (tùy chọn)
                    order.payment_link = create_payment_result_obj.checkoutUrl
                    order.save(update_fields=['payment_link'])
                    return redirect(create_payment_result_obj.checkoutUrl)
                else:
                    logger.error(f"PayOS: checkoutUrl is invalid for order {order.order_id}. Obj: {create_payment_result_obj}")
                    messages.error(request, "Lỗi tạo link: URL thanh toán không hợp lệ từ PayOS.")
                    order.status = "PayError"; order.save(update_fields=['status'])

            except PayOSError as pe:
                logger.error(f"PayOS API Error for order {order.order_id}: Code {pe.code}, Message: {str(pe)}")
                messages.error(request, f"Lỗi từ PayOS: {str(pe)} (Mã: {pe.code})")
                order.status = "PayError"; order.save(update_fields=['status'])
            except Exception as e:
                logger.exception(f"General Error (PayOS link creation) for order {order.order_id}: {str(e)}")
                messages.error(request, f"Lỗi không mong muốn khi tạo yêu cầu TT: {str(e)}. Thử lại...")
                order.status = "PayError"; order.save(update_fields=['status'])
            
            return render(request, 'checkout.html', {'checkout_items': valid_items_for_checkout, 'total': checkout_total_price, 'form_data': request.POST})
        
        elif payment_method == 'cod':
            with transaction.atomic():
                # Logic này nên được chuyển vào webhook nếu COD cũng cần xác nhận từ bên thứ 3
                # Hiện tại, giả sử COD được xác nhận ngay
                for entry in valid_items_for_checkout:
                    product_to_update = entry['product_obj']
                    # Re-fetch product inside transaction to lock the row
                    product_to_update = Product.objects.select_for_update().get(pk=product_to_update.pk)
                    if product_to_update.quantity_in_stock >= entry['quantity']:
                        product_to_update.quantity_in_stock -= entry['quantity']
                        product_to_update.save(update_fields=['quantity_in_stock'])
                    else:
                        messages.error(request, f"Xin lỗi, '{product_to_update.product_name}' không còn đủ số lượng.")
                        # Giao dịch sẽ tự rollback, không cần set status Failed
                        raise Exception("Stock not sufficient") 
                
                Cart.objects.filter(user=request.user.username).delete()
                order.status = 'Confirmed'; order.save(update_fields=['status'])
                messages.success(request, 'Đơn hàng (COD) đã được đặt thành công!')
                return redirect('products:orders_get')
        
    return render(request, 'checkout.html', {'checkout_items': valid_items_for_checkout, 'total': checkout_total_price})
def cart_delete(request, pid):
    if not request.user.is_authenticated: return redirect('login') 
    if request.user.is_superuser: return HttpResponse("Invalid Action for Admin")
    product_instance = get_object_or_404(Product, product_id=pid)
    Cart.objects.filter(user=request.user.username, product=product_instance).delete()
    messages.info(request, f"'{product_instance.product_name}' đã được xóa khỏi giỏ hàng.")
    return redirect('products:cart_get') 

def order_cancel(request, oid):
    """
    Sửa lỗi: Khi người dùng tự hủy đơn hàng đang chờ, chỉ đổi trạng thái,
    KHÔNG hoàn kho vì kho chưa bị trừ.
    """
    if not request.user.is_authenticated: return redirect('login')
    try:
        order_id_int = int(oid)
    except ValueError:
        messages.error(request, "ID đơn hàng không hợp lệ."); return redirect('products:orders_get')
    
    if request.user.is_superuser:
        messages.error(request, "Admin nên quản lý đơn hàng qua trang chi tiết đơn hàng.")
        return redirect('products:orders_get')
        
    order_to_cancel = get_object_or_404(Orders, order_id=order_id_int, user=request.user.username)
    
    # Chỉ cho phép hủy các đơn hàng đang chờ xử lý hoặc chờ thanh toán
    if order_to_cancel.status in ['Pending', 'PendPay']: 
        order_to_cancel.status = 'Canceled'
        order_to_cancel.save(update_fields=['status'])
        # --- ĐÃ LOẠI BỎ HOÀN TOÀN LOGIC HOÀN KHO BỊ LỖI ---
        messages.success(request, f"Đơn hàng #{oid} đã được hủy thành công.")
    else:
        messages.error(request, f"Không thể hủy đơn hàng #{oid} với trạng thái hiện tại ('{order_to_cancel.get_status_display()}').")
    
    return redirect('products:orders_get')


# products/views.py

def order_details(request, oid):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        order_id_int = int(oid)
    except ValueError:
        messages.error(request, "ID đơn hàng không hợp lệ.")
        return redirect('products:orders_get')

    # Xây dựng câu truy vấn an toàn, get_object_or_404 sẽ xử lý việc tìm kiếm
    # Superuser có thể xem mọi đơn hàng, người dùng thường chỉ xem đơn của mình
    if request.user.is_superuser:
        order_instance = get_object_or_404(Orders, order_id=order_id_int)
    else:
        order_instance = get_object_or_404(Orders, order_id=order_id_int, user=request.user.username)

    # === DÒNG QUAN TRỌNG ĐÃ SỬA LỖI ===
    # Thay 'product_id' thành 'product'
    details_for_order = OrderDetails.objects.filter(
        order=order_instance
    ).select_related(
        'product'  # Sử dụng tên trường ForeignKey là 'product'
    ).prefetch_related(
        'review'   # Dùng prefetch cho quan hệ ngược từ OrderDetail -> Review
    )
    # ==================================

    order_items_with_review_status = []
    allowed_statuses_for_review = ['Delivered'] 
    can_review_order_overall = order_instance.status in allowed_statuses_for_review
    
    for detail in details_for_order:
        # Kiểm tra xem sản phẩm có tồn tại không (do on_delete=SET_NULL)
        is_reviewed = hasattr(detail, 'review') and detail.review is not None
        can_review_item = detail.product is not None and not is_reviewed and can_review_order_overall
        order_items_with_review_status.append({
            'detail': detail, 
            'is_reviewed': is_reviewed, 
            'can_review_item': can_review_item
        })

    context = {
        'order': order_instance, 
        'order_items_with_review_status': order_items_with_review_status, 
        'id': order_id_int, 
        'status': order_instance.status, 
        'total': order_instance.total_price
    }

    return render(request, 'order_details.html', context)

# --- HÀM TRUY XUẤT SẢN PHẨM (RETRIEVAL) CHO RAG ---
# --- HÀM TRUY XUẤT SẢN PHẨM (RETRIEVAL) CHO RAG (PHIÊN BẢN CẢI TIẾN) ---
def find_relevant_products(user_query, max_results=3):
    """
    Tìm kiếm các sản phẩm trong CSDL có liên quan đến câu hỏi của người dùng.
    Đã được cải tiến để xử lý các câu hỏi chung chung.
    """
    lower_query = user_query.lower()
    
    # 1. Nhận diện các câu hỏi chung chung, mang tính khám phá
    generic_query_starters = [
        "shop có gì", "shop bán gì", "bán những gì", "có sản phẩm nào", 
        "xem sản phẩm", "cho xem", "có gì bán không", "tư vấn sản phẩm"
    ]
    is_generic_query = any(starter in lower_query for starter in generic_query_starters)

    if is_generic_query:
        # Với câu hỏi chung, gợi ý các sản phẩm mới nhất còn hàng
        logger.info(f"RAG: Detected a generic query: '{user_query}'. Fetching latest products.")
        try:
            return list(Product.objects.filter(quantity_in_stock__gt=0).order_by('-product_id')[:max_results])
        except Exception as e:
            logger.error(f"Error fetching latest products for generic query: {e}")
            return []

    # 2. Nếu không phải câu hỏi chung, tiếp tục logic tìm kiếm từ khóa như cũ
    keywords = lower_query.split()
    meaningful_keywords = [kw for kw in keywords if len(kw) > 2 and kw not in [
        "là", "có", "giá", "bao", "nhiêu", "một", "cho", "tôi", "xem", "sản", "phẩm", "về"
    ]]

    if not meaningful_keywords:
        # Nếu không có từ khóa ý nghĩa, có thể trả về danh sách rỗng hoặc gợi ý chung
        logger.info(f"RAG: No meaningful keywords found in '{user_query}'.")
        return []

    logger.info(f"RAG: Searching for keywords: {meaningful_keywords}")
    query_conditions = Q()
    for keyword in meaningful_keywords:
        query_conditions |= Q(product_name__icontains=keyword)
        query_conditions |= Q(product_description__icontains=keyword)
        query_conditions |= Q(company__icontains=keyword)

    try:
        products = Product.objects.filter(query_conditions).distinct().order_by('-product_id')[:max_results]
        return list(products)
    except Exception as e:
        logger.error(f"Error querying products for RAG with keywords '{meaningful_keywords}': {e}")
        return []

# --- HÀM TẠO BỐI CẢNH TỪ SẢN PHẨM (AUGMENTATION) CHO RAG ---
def create_product_context_for_gemini(products):
    """
    Tạo một chuỗi bối cảnh từ danh sách các đối tượng Product để cung cấp cho Gemini.
    """
    if not products:
        return ""

    context_parts = ["Dưới đây là một số thông tin sản phẩm từ cửa hàng của chúng tôi có thể liên quan đến câu hỏi của bạn:"]
    for i, product in enumerate(products):
        part = f"\nSản phẩm {i+1}:\n"
        part += f"- Tên: {product.product_name} (Mã: {product.product_id})\n"
        part += f"- Hãng sản xuất: {product.company}\n"
        part += f"- Giá bán: {product.sell_price} vnd\n" # Giả sử đơn vị $
        
        desc_snippet = product.product_description
        if len(desc_snippet) > 150: # Giới hạn mô tả
            desc_snippet = desc_snippet[:150] + "..."
        part += f"- Mô tả: {desc_snippet}\n"
        
        status = "Còn hàng" if product.quantity_in_stock > 0 else "Hết hàng"
        part += f"- Tình trạng: {status} (Số lượng còn lại: {product.quantity_in_stock})"
        context_parts.append(part)
    
    context_parts.append("\n\nVui lòng sử dụng thông tin trên để trả lời câu hỏi của khách hàng một cách chính xác và hữu ích. Nếu không có thông tin nào hoàn toàn phù hợp, hãy cho biết bạn không tìm thấy sản phẩm đáp ứng chính xác yêu cầu trong dữ liệu hiện có và có thể gợi ý các sản phẩm tương tự nếu có.")
    return "\n".join(context_parts)

# --- VIEW CHAT VỚI GEMINI (CÓ TÍCH HỢP RAG) ---
def gemini_chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message_original = data.get('message')

            if not user_message_original:
                return JsonResponse({'error': 'No message provided'}, status=400)

            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                logger.error("GEMINI_API_KEY not configured in environment variables or .env file.")
                return JsonResponse({'error': 'AI service not configured (API key missing).'}, status=500)

            # RAG: Truy xuất sản phẩm và tạo bối cảnh
            relevant_products = find_relevant_products(user_message_original)
            product_context_for_llm = create_product_context_for_gemini(relevant_products)
            
            system_prompt = "Bạn là một trợ lý AI thông minh và thân thiện của một cửa hàng trực tuyến. Hãy trả lời câu hỏi của khách hàng một cách lịch sự, cung cấp thông tin chính xác dựa trên dữ liệu được cung cấp nếu có. Nếu không chắc chắn hoặc không có thông tin, hãy nói rõ điều đó.Khi trả lời các câu hỏi liên quan đến giá, hãy luôn sử dụng đơn vị Việt Nam Dồng VND. Hãy luôn đưa ra các sản phẩm hiện có tại cửa hàng và chào mời khách mua hàng."
            
            final_prompt_parts = [system_prompt]
            if product_context_for_llm:
                final_prompt_parts.append(product_context_for_llm)
            final_prompt_parts.append(f"\nCâu hỏi từ khách hàng:\n{user_message_original}")
            
            final_prompt_for_gemini = "\n\n".join(final_prompt_parts)
            # logger.info(f"Final prompt for Gemini:\n---\n{final_prompt_for_gemini}\n---") # Log để debug

            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}" # Sử dụng gemini-1.5-flash-latest
            
            payload = {
                "contents": [{"parts": [{"text": final_prompt_for_gemini}]}],
                "generationConfig": {
                    "temperature": 0.6, 
                    "maxOutputTokens": 1500, 
                    "topP": 0.9,
                    "topK": 40 
                },
                "safetySettings": [ # Thêm cài đặt an toàn cơ bản
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            }
            headers = {'Content-Type': 'application/json'}

            response = requests.post(gemini_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status() # Ném lỗi cho HTTP status 4xx/5xx
            
            response_data = response.json()
            # logger.info(f"Gemini API Response: {json.dumps(response_data, indent=2)}")

            ai_reply = "Xin lỗi, tôi chưa thể xử lý yêu cầu của bạn lúc này." # Default reply
            if 'candidates' in response_data and response_data['candidates']:
                candidate = response_data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content'] and candidate['content']['parts']:
                    ai_reply = candidate['content']['parts'][0]['text']
                elif 'finishReason' in candidate and candidate['finishReason'] != 'STOP':
                    logger.warning(f"Gemini generation finished with reason: {candidate['finishReason']}. Candidate: {candidate}")
                    ai_reply = f"Tôi gặp một chút vấn đề khi tạo phản hồi (Lý do: {candidate['finishReason']}). Bạn có thể thử lại hoặc hỏi khác đi không?"
            elif 'promptFeedback' in response_data and 'blockReason' in response_data['promptFeedback']:
                block_reason = response_data['promptFeedback']['blockReason']
                logger.warning(f"Gemini API blocked prompt. Reason: {block_reason}. Feedback: {response_data['promptFeedback']}")
                ai_reply = f"Rất tiếc, yêu cầu của bạn không thể được xử lý do chính sách nội dung. (Lý do: {block_reason})"
            
            return JsonResponse({'reply': ai_reply.strip()})

        except json.JSONDecodeError:
            logger.warning("Invalid JSON received in chat request body.")
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out.")
            return JsonResponse({'error': 'AI service request timed out.'}, status=504)
        except requests.exceptions.RequestException as e:
            error_message_log = str(e)
            status_code_for_client = 502 # Bad Gateway
            client_error_message = 'Lỗi kết nối đến dịch vụ AI.'
            if e.response is not None:
                logger.error(f"Gemini API request failed with status {e.response.status_code}. Response: {e.response.text}")
                error_message_log = f"Status: {e.response.status_code}, Response: {e.response.text}"
                if e.response.status_code == 400: # Bad Request (thường do prompt sai định dạng hoặc API key)
                    status_code_for_client = 400
                    try:
                        err_details = e.response.json()
                        client_error_message = err_details.get("error", {}).get("message", "Yêu cầu không hợp lệ đến dịch vụ AI.")
                    except json.JSONDecodeError:
                        client_error_message = "Yêu cầu không hợp lệ đến dịch vụ AI."
                elif e.response.status_code == 429: # Rate limit
                     status_code_for_client = 429
                     client_error_message = "Dịch vụ AI đang quá tải, vui lòng thử lại sau."
            else:
                logger.error(f"Gemini API request failed (no response object): {e}")
            
            return JsonResponse({'error': client_error_message}, status=status_code_for_client)
        except Exception as e:
            logger.exception(f"Unexpected error in gemini_chat_view: {e}")
            return JsonResponse({'error': 'Đã xảy ra lỗi không mong muốn trên máy chủ.'}, status=500)

    return JsonResponse({'error': 'Chỉ chấp nhận yêu cầu POST.'}, status=405)
# products/views.py
def add_product_review(request, order_detail_id):
    """
    Sửa lỗi hoàn toàn: Dùng `product` và `order` thay vì `product_id`, `order_id`
    """
    if not request.user.is_authenticated or request.user.is_superuser:
        messages.error(request, "Vui lòng đăng nhập với tài khoản khách hàng để đánh giá sản phẩm."); return redirect('login')
    
    # Lấy chi tiết đơn hàng và các đối tượng liên quan trong 1 câu query
    order_detail = get_object_or_404(
        OrderDetails.objects.select_related('order', 'product'), 
        pk=order_detail_id, 
        order__user=request.user.username
    )

    # Lấy order và product từ order_detail đã truy vấn
    order = order_detail.order
    product = order_detail.product

    if not product:
        messages.error(request, "Không thể đánh giá vì sản phẩm này không còn tồn tại."); return redirect('products:order_details', oid=order.order_id)
    
    if order.status != 'Delivered':
        messages.error(request, "Chỉ có thể đánh giá các sản phẩm trong đơn hàng đã được giao thành công."); return redirect('products:order_details', oid=order.order_id)
    
    if ProductReview.objects.filter(order_detail=order_detail).exists():
        messages.info(request, f"Bạn đã đánh giá sản phẩm '{product.product_name}' cho đơn hàng này rồi."); return redirect('products:product_details', pid=product.product_id)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order_detail = order_detail
            review.save()
            messages.success(request, f"Cảm ơn bạn đã đánh giá sản phẩm '{product.product_name}'!"); 
            return redirect('products:product_details', pid=product.product_id)
        else:
            messages.error(request, "Thông tin bạn nhập không hợp lệ, vui lòng kiểm tra lại.")
    else:
        form = ProductReviewForm()
        
    context = {'form': form, 'product': product, 'order_detail': order_detail, 'order': order}
    return render(request, 'products/add_review.html', context)

@csrf_exempt
def payment_webhook_receiver(request):
    if request.method == 'POST':
        if not payos_client:
            logger.error("PayOS client not initialized. Cannot process webhook.")
            return JsonResponse({'error': 'Payment service not configured'}, status=500)
        
        try:
            webhook_data_raw = request.body
            webhook_data = json.loads(webhook_data_raw)
            logger.info(f"Received PayOS webhook: {json.dumps(webhook_data, indent=2)}")

            # BỎ QUA VIỆC XÁC MINH CHỮ KÝ TRONG MÔI TRƯỜNG TEST
            # TRONG PRODUCTION, BẠN BẮT BUỘC PHẢI XÁC MINH CHỮ KÝ
            # signature = request.headers.get('Payos-Signature')
            # if not signature:
            #     return JsonResponse({'error': 'Missing signature'}, status=401)
            # try:
            #     payos_client.verifyWebhookData(webhook_data, signature)
            # except PayOSError:
            #     return JsonResponse({'error': 'Invalid signature'}, status=401)

            order_code_from_webhook = webhook_data.get('orderCode')
            webhook_event_code = webhook_data.get('code')

            if not order_code_from_webhook:
                logger.error(f"Webhook data missing 'orderCode': {webhook_data}")
                return JsonResponse({'code': '99', 'desc': 'Missing orderCode'}, status=400)

            with transaction.atomic():
                try:
                    # SỬA Ở ĐÂY: Tìm đơn hàng bằng trường `payment_order_code`
                    order = Orders.objects.select_for_update().get(payment_order_code=int(order_code_from_webhook))
                except Orders.DoesNotExist:
                    logger.error(f"Order with payment_order_code {order_code_from_webhook} not found for PayOS webhook.")
                    return JsonResponse({'code': '02', 'desc': 'Order not found'}, status=200) # PayOS yêu cầu trả về 200
                except (ValueError, TypeError):
                    logger.error(f"Invalid order_code format from PayOS webhook: {order_code_from_webhook}")
                    return JsonResponse({'code': '99', 'desc': 'Invalid orderCode format'}, status=400)

                if order.status not in ['Pending', 'PendPay', 'PayError']:
                    logger.info(f"Order {order.order_id} (status: {order.status}) already processed. Webhook for code {order_code_from_webhook} ignored.")
                    return JsonResponse({'code': '00', 'desc': 'Success (Order already appropriately processed)'}, status=200)

                if webhook_event_code == '00': # Giao dịch thành công
                    order.status = 'Confirmed'
                    all_items_in_stock = True
                    order_details_items = OrderDetails.objects.filter(order=order).select_related('product')
                    
                    for detail in order_details_items:
                        product_to_update = detail.product
                        if product_to_update and product_to_update.quantity_in_stock >= detail.quantity:
                            product_to_update.quantity_in_stock -= detail.quantity
                            product_to_update.save(update_fields=['quantity_in_stock'])
                        else:
                            logger.error(f"Product {product_to_update.product_id if product_to_update else 'N/A'} is out of stock for order {order.order_id}. Setting status to StockErr.")
                            order.status = 'StockErr' # Hết hàng, cần hoàn tiền
                            all_items_in_stock = False
                            break
                    
                    if all_items_in_stock:
                        Cart.objects.filter(user=order.user).delete()
                        logger.info(f"Order {order.order_id} payment successful. Status set to {order.status}. Cart cleared.")
                    else:
                        logger.error(f"Order {order.order_id} paid but had a stock issue. Status set to {order.status}.")
                    
                    # Lưu lại mã giao dịch của PayOS nếu có
                    if webhook_data.get('data') and webhook_data['data'].get('paymentLinkId'):
                         order.payment_id = webhook_data['data']['paymentLinkId']
                    
                    order.save(update_fields=['status', 'payment_id'])
                else: # Giao dịch thất bại hoặc bị hủy
                    logger.info(f"Order {order.order_id} webhook event code '{webhook_event_code}'. Setting status to Failed.")
                    order.status = 'Failed'
                    order.save(update_fields=['status'])
            
            return JsonResponse({'code': '00', 'desc': 'Success'}, status=200)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in PayOS webhook request body.")
            return JsonResponse({'code': '99', 'desc': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.exception(f"Error processing PayOS webhook: {str(e)}")
            return JsonResponse({'code': '99', 'desc': 'Internal server error'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# ... các import và các hàm khác giữ nguyên ...
from django.conf import settings # Đảm bảo đã import settings
from django.db import transaction # Đảm bảo đã import transaction

# ...

# products/views.py

def payment_return_page(request):
    """
    Xử lý khi người dùng được PayOS chuyển hướng về.
    Sửa lại để tìm đơn hàng bằng `payment_order_code`.
    """
    order_code_from_gateway_str = request.GET.get('orderCode')
    status_from_gateway = request.GET.get('status')
    code_from_gateway = request.GET.get('code')

    if not order_code_from_gateway_str:
        messages.error(request, "Không tìm thấy thông tin đơn hàng từ trang thanh toán.")
        return redirect('products:orders_get')

    try:
        # TÌM ĐƠN HÀNG BẰNG `payment_order_code` MÀ PAYOS TRẢ VỀ
        order_code_int = int(order_code_from_gateway_str)
        order = Orders.objects.get(payment_order_code=order_code_int)

        # =======================================================================
        # === BLOCK TỰ ĐỘNG XỬ LÝ CHO MÔI TRƯỜNG TEST (DEBUG=True) ===
        # Khối này mô phỏng webhook, giúp cập nhật trạng thái ngay lập tức khi test.
        # =======================================================================
        if settings.DEBUG and code_from_gateway == '00' and status_from_gateway == 'PAID':
            logger.warning(f"[DEBUG MODE] Simulating successful webhook for order_id {order.order_id} via payment_order_code {order_code_int}.")
            
            # Chỉ mô phỏng nếu đơn hàng đang ở trạng thái chờ thanh toán
            if order.status in ['PendPay', 'PayError']:
                with transaction.atomic():
                    # Lấy lại đối tượng order với select_for_update để khóa dòng
                    order_to_update = Orders.objects.select_for_update().get(pk=order.pk)
                    
                    # Logic giống hệt như trong webhook thật
                    order_to_update.status = 'Confirmed'
                    all_items_in_stock = True
                    # Sửa lại query để lấy đúng chi tiết đơn hàng
                    order_details_items = OrderDetails.objects.filter(order=order_to_update).select_related('product')
                    
                    for detail in order_details_items:
                        product = detail.product # Lấy đúng đối tượng product
                        if product and product.quantity_in_stock >= detail.quantity:
                            product.quantity_in_stock -= detail.quantity
                            product.save(update_fields=['quantity_in_stock'])
                        else:
                            order_to_update.status = 'StockErr'
                            all_items_in_stock = False
                            logger.error(f"[DEBUG MODE] Stock issue for product {product.product_id if product else 'N/A'} in order {order.order_id}.")
                            break
                    
                    if all_items_in_stock:
                        Cart.objects.filter(user=order_to_update.user).delete()
                        logger.info(f"[DEBUG MODE] Order {order.order_id} status set to Confirmed. Cart cleared.")
                    
                    order_to_update.save(update_fields=['status'])
                    
                    # Gán lại biến `order` để phần dưới của hàm thấy được trạng thái mới
                    order = order_to_update 
                    messages.success(request, f"[Chế độ Test] Đơn hàng #{order.order_id} đã được tự động xác nhận thành công.")
            else:
                 logger.info(f"[DEBUG MODE] Order {order.order_id} already in status '{order.status}'. No simulation needed.")

        # =======================================================================
        # === KẾT THÚC BLOCK TỰ ĐỘNG XỬ LÝ ===
        # =======================================================================

        # Logic hiển thị thông báo cho người dùng (chạy trong cả môi trường test và production)
        if code_from_gateway == '00' and status_from_gateway == 'PAID':
            # Sau khi khối debug chạy, order.status đã là 'Confirmed' hoặc 'StockErr'
            if order.status == 'Confirmed' or order.status == 'Processing':
                messages.success(request, f"Thanh toán cho đơn hàng #{order.order_id} thành công!")
            elif order.status == 'StockErr':
                messages.error(request, f"Thanh toán cho đơn hàng #{order.order_id} thành công, nhưng đã xảy ra lỗi về kho hàng. Vui lòng liên hệ hỗ trợ để được hoàn tiền.")
            else:
                # Trường hợp webhook chưa kịp chạy
                messages.info(request, f"Giao dịch cho đơn hàng #{order.order_id} đã được ghi nhận. Hệ thống đang cập nhật trạng thái.")
        
        elif status_from_gateway == 'CANCELLED':
            messages.warning(request, f"Bạn đã hủy thanh toán cho đơn hàng #{order.order_id}.")
            if order.status == 'PendPay': 
                order.status = 'Canceled'
                order.save(update_fields=['status'])
        
        else: # Các trường hợp lỗi khác
            error_message_from_gateway = request.GET.get('message', f"Lỗi từ cổng thanh toán (mã {code_from_gateway})")
            messages.error(request, f"Giao dịch cho đơn hàng #{order.order_id} không thành công: {error_message_from_gateway}")
            if order.status == 'PendPay': 
                order.status = 'PayError'
                order.save(update_fields=['status'])

        # Chuyển hướng người dùng đến trang chi tiết đơn hàng của họ
        return redirect('products:order_details', oid=order.order_id)

    except Orders.DoesNotExist:
        messages.error(request, f"Đơn hàng với mã giao dịch #{order_code_from_gateway_str} không tồn tại.")
        return redirect('products:orders_get')
    except (ValueError, TypeError):
        messages.error(request, "Mã đơn hàng từ cổng thanh toán không hợp lệ.")
        return redirect('products:orders_get')
    except Exception as e:
        logger.exception(f"Lỗi nghiêm trọng khi xử lý trả về từ PayOS cho mã {order_code_from_gateway_str}: {e}")
        messages.error(request, "Lỗi xử lý kết quả thanh toán. Vui lòng kiểm tra lại đơn hàng của bạn.")
        return redirect('products:orders_get')

def payment_cancel_page(request):
    """
    Sửa lỗi: Khi hủy thanh toán từ PayOS, chỉ đổi trạng thái đơn hàng,
    KHÔNG hoàn kho vì kho chưa bị trừ.
    """
    order_code_str = request.GET.get('orderCode')
    if order_code_str:
        try:
            order_code = int(order_code_str)
            order = Orders.objects.get(payment_order_code=order_code)
            
            messages.warning(request, f"Bạn đã hủy thanh toán cho đơn hàng #{order.order_id}.")

            if order.status == 'PendPay':
                order.status = 'Canceled'
                order.save(update_fields=['status'])
                # --- ĐÃ LOẠI BỎ HOÀN TOÀN LOGIC HOÀN KHO BỊ LỖI ---
            
        except (Orders.DoesNotExist, ValueError, TypeError): 
            messages.error(request, f"Không tìm thấy đơn hàng tương ứng với giao dịch đã hủy.")
    else:
        messages.info(request, "Giao dịch thanh toán đã được hủy.")
    
    # Chuyển về giỏ hàng để người dùng có thể checkout lại
    return redirect('products:cart_get')
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser, login_url='/accounts/login/')
def admin_change_order_status(request, oid, action):
    """
    View cho phép admin thay đổi trạng thái của một đơn hàng.
    """
    order = get_object_or_404(Orders, order_id=oid)
    
    # Định nghĩa các bước chuyển trạng thái hợp lệ
    valid_transitions = {
        'Confirmed': ['process'],           # Từ Confirmed chỉ có thể sang Processing
        'Processing': ['ship'],             # Từ Processing chỉ có thể sang Shipped
        'Shipped': ['deliver'],             # Từ Shipped chỉ có thể sang Delivered
    }
    
    current_status = order.status
    
    if current_status in valid_transitions and action in valid_transitions[current_status]:
        if action == 'process':
            order.status = 'Processing'
            messages.success(request, f"Đơn hàng #{oid} đã được chuyển sang trạng thái 'Đang xử lý'.")
        elif action == 'ship':
            order.status = 'Shipped'
            messages.success(request, f"Đơn hàng #{oid} đã được chuyển sang trạng thái 'Đã vận chuyển'.")
        elif action == 'deliver':
            order.status = 'Delivered'
            messages.success(request, f"Đơn hàng #{oid} đã được chuyển sang trạng thái 'Đã giao hàng'. Giờ khách hàng có thể đánh giá.")
        
        order.save(update_fields=['status'])
    else:
        messages.error(request, f"Hành động '{action}' không hợp lệ cho đơn hàng #{oid} với trạng thái hiện tại là '{order.get_status_display()}'.")
        
    return redirect('products:order_details', oid=oid)