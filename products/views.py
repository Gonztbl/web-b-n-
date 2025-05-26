# products/views.py
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.utils.html import escape
from django.shortcuts import render, redirect, get_object_or_404
import logging

from .models import Product, Cart, Orders, OrderDetails
from .forms import ProductForm
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

def product_edit(request, pid):
    product = get_object_or_404(Product, product_id=pid)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product, is_edit=True) # Pass is_edit
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('products:product_list') # MODIFIED HERE
    else:
        form = ProductForm(instance=product, is_edit=True) # Pass is_edit
    
    return render(request, 'products/product_add.html', {
        'form': form, 
        'product': product, 
        'url': request.path, # For form action
        'is_edit': True # Flag for template
    })

def product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES) # is_edit is False by default in form
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('products:product_list') # MODIFIED HERE
    else:
        form = ProductForm() # is_edit is False by default in form
    return render(request, 'products/product_add.html', {
        'form': form, 
        'product': None, # No existing product instance for add
        'url': request.path, # For form action
        'is_edit': False # Flag for template
    })

def home(request):
    """ Render product page (which is the main product list page) """
    return render(request, 'index.html')


def product_list(request): # This is the main products display page
    pds_query = Product.objects.all()

    pname_q = request.GET.get("pname", "").strip()
    filter_q = request.GET.get("filter", "").strip()
    sort_q = request.GET.get("sort", "").strip()

    if pname_q:
        pds_query = pds_query.filter(product_name__icontains=pname_q)

    if filter_q == 'avail':
        pds_query = pds_query.filter(quantity_in_stock__gt=0)
    elif filter_q == 'sold-out':
        pds_query = pds_query.filter(quantity_in_stock=0)

    if sort_q == 'name-a-to-z':
        pds_query = pds_query.order_by('product_name')
    elif sort_q == 'name-z-to-a':
        pds_query = pds_query.order_by('-product_name')
    elif sort_q == 'price-up':
        pds_query = pds_query.order_by('sell_price')
    elif sort_q == 'price-down':
        pds_query = pds_query.order_by('-sell_price')
    else: # Default sort
        pds_query = pds_query.order_by('product_id')


    paginator = Paginator(pds_query, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'count': pds_query.count(),
        'query_pname': pname_q,     
        'query_filter': filter_q,   
        'query_sort': sort_q,       
    }
    return render(request, 'products/product.html', context)


def product_search(request):
    query_params = request.GET.copy()
    if not query_params: 
        return redirect('products:product_list') # MODIFIED HERE
        
    # Use reverse to build the URL with namespace
    from django.urls import reverse
    list_url = reverse('products:product_list')
    return redirect(f"{list_url}?{query_params.urlencode()}")


def product_details(request, pid):
    product = get_object_or_404(Product, product_id=pid)
    display_quantity_in_cart = 0 

    if request.user.is_authenticated and not request.user.is_superuser:
        try:
            cart_item = Cart.objects.get(user=request.user.username, product=product)
            display_quantity_in_cart = cart_item.quantity
        except Cart.DoesNotExist:
            display_quantity_in_cart = 0
            
    return render(request, 'products/product_details.html', {'product': product, 'quantity': display_quantity_in_cart})

def cart_add(request, pid):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to add items to your cart.")
        return redirect('login') 

    if request.user.is_superuser:
        messages.error(request, "Admin users cannot add items to the cart.")
        return redirect('products:product_list') 

    storage = messages.get_messages(request)
    storage.used = True 

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
        if deleted_count > 0:
            messages.info(request, f'{product_instance.product_name} has been removed from your cart.')
        return redirect('products:product_details', pid=pid) 

    cart_item, created = Cart.objects.get_or_create(
        user=user_username, 
        product=product_instance,
        defaults={'quantity': 0} 
    )
    
    if quantity_desired > product_instance.quantity_in_stock:
        messages.warning(request, f"Sorry, we only have {product_instance.quantity_in_stock} of {product_instance.product_name} in stock. Your cart quantity cannot exceed this amount.")
        if product_instance.quantity_in_stock > 0 :
            if cart_item.quantity != product_instance.quantity_in_stock: 
                cart_item.quantity = product_instance.quantity_in_stock
                cart_item.save()
                messages.info(request, f"Quantity for {product_instance.product_name} has been set to the maximum available: {product_instance.quantity_in_stock}.")
        elif cart_item.pk: 
             cart_item.delete()
             messages.info(request, f"{product_instance.product_name} is out of stock and was removed from your cart.")
    else:
        if cart_item.quantity != quantity_desired: 
            cart_item.quantity = quantity_desired
            cart_item.save()
            if created and quantity_desired > 0:
                messages.success(request, f'Added {quantity_desired} of {product_instance.product_name} to your cart!')
            elif not created and quantity_desired > 0:
                messages.success(request, f'Updated quantity of {product_instance.product_name} in your cart to {quantity_desired}.')
    
    return redirect('products:product_details', pid=pid) 

def cart_get(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    if request.user.is_superuser:
        messages.error(request, "Admin users do not have a cart.")
        return redirect('products:product_list') # MODIFIED HERE

    user_cart_items_query = Cart.objects.filter(user=request.user.username).select_related('product')
    processed_cart_items_list = [] 
    stock_changed_flag = False 

    logger.info(f"--- Starting cart processing for user: {request.user.username} ---")

    for item in user_cart_items_query:
        logger.debug(f"Processing Cart item pk={item.pk}, raw product_id FK: {item.product_id}")
        
        product_object = None
        try:
            if hasattr(item, 'product') and isinstance(item.product, Product):
                product_object = item.product
                logger.debug(f"Cart pk={item.pk}: item.product is a Product instance: {product_object.product_name} (ID: {product_object.product_id})")
                if not hasattr(product_object, 'sell_price'): 
                    logger.error(f"Cart pk={item.pk}: Product object {product_object.product_id} LACKS sell_price attribute! Deleting cart item.")
                    messages.error(request, f"Product '{str(product_object)}' in your cart has missing price data and was removed.")
                    item.delete()
                    stock_changed_flag = True
                    continue
            else:
                logger.warning(f"Cart pk={item.pk}: item.product is NOT a Product instance. Type: {type(item.product)}, Value: '{item.product}'. Attempting manual fetch using FK: {item.product_id}.")
                try:
                    product_object = Product.objects.get(product_id=item.product_id) 
                    logger.info(f"Cart pk={item.pk}: Manually fetched product: {product_object.product_name} (ID: {product_object.product_id})")
                except Product.DoesNotExist:
                    logger.error(f"Cart pk={item.pk}: Product with id '{item.product_id}' (from cart's FK) does not exist. Deleting cart item.")
                    messages.error(request, f"A cart item for product ID '{item.product_id}' (which no longer exists) was found and removed.")
                    item.delete()
                    stock_changed_flag = True
                    continue
        
        except Exception as e: 
            logger.exception(f"Cart pk={item.pk}: Unexpected error processing product relation: {e}. Deleting cart item.")
            messages.error(request, "An unexpected error occurred with an item in your cart. It has been removed.")
            item.delete()
            stock_changed_flag = True
            continue

        if product_object is None: 
            logger.error(f"Cart pk={item.pk}: product_object is None after checks. This is unexpected. Skipping item.")
            continue

        if product_object.quantity_in_stock == 0:
            logger.info(f"Cart pk={item.pk}: Product '{product_object.product_name}' is out of stock. Deleting cart item.")
            messages.warning(request, f"{product_object.product_name} was removed from your cart as it's no longer in stock.")
            item.delete()
            stock_changed_flag = True
        elif item.quantity > product_object.quantity_in_stock:
            logger.info(f"Cart pk={item.pk}: Quantity for '{product_object.product_name}' ({item.quantity}) exceeds stock ({product_object.quantity_in_stock}). Adjusting.")
            messages.info(request, f"Quantity of {product_object.product_name} in your cart was adjusted to {product_object.quantity_in_stock} due to stock changes.")
            item.quantity = product_object.quantity_in_stock
            item.save(update_fields=['quantity'])
            processed_cart_items_list.append({'cart_item_obj': item, 'product_obj': product_object, 'quantity': item.quantity})
            stock_changed_flag = True
        else:
            logger.debug(f"Cart pk={item.pk}: Product '{product_object.product_name}' is OK. Adding to processed list.")
            processed_cart_items_list.append({'cart_item_obj': item, 'product_obj': product_object, 'quantity': item.quantity})

    logger.info(f"--- Finished cart processing. Number of displayable items: {len(processed_cart_items_list)} ---")
            
    current_total_price = sum(entry['product_obj'].sell_price * entry['quantity'] for entry in processed_cart_items_list)
    
    return render(request, 'cart.html', {
        'cart_entries': processed_cart_items_list,
        'changed': stock_changed_flag, 
        'total': current_total_price
        })

def orders_get(request):
    if not request.user.is_authenticated:
        return redirect('login') 

    orders_list_query = None
    if request.user.is_superuser:
        orders_list_query = Orders.objects.all()
    else:
        orders_list_query = Orders.objects.filter(user=request.user.username)
    
    status_filter_from_url = request.GET.get('status', '').strip()
    
    if status_filter_from_url:
        model_status_filter = None
        # Make sure to match the value attribute in order.html's select options
        for val, display_name in Orders.ORDER_STATUS_CHOICES:
            if status_filter_from_url == val.lower(): # e.g. 'confirmed' should match 'Confirmed'
                model_status_filter = val
                break
        
        if model_status_filter:
            orders_list_query = orders_list_query.filter(status=model_status_filter)
    
    orders_list_query = orders_list_query.order_by('-order_id')
            
    return render(request, 'order.html', {
        'orders': orders_list_query,
        'user_order_status_choices': Orders.ORDER_STATUS_CHOICES # For admin filter dropdown
        })


def cart_checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        messages.error(request, "Admin users cannot checkout.")
        return redirect('products:product_list') # MODIFIED HERE

    storage = messages.get_messages(request)
    storage.used = True

    user_cart_items_query = Cart.objects.filter(user=request.user.username).select_related('product')
    valid_items_for_checkout = []
    checkout_total_price = 0
    cart_issues_found = False 

    for item in user_cart_items_query:
        product_object = None
        try: 
            if hasattr(item, 'product') and isinstance(item.product, Product): product_object = item.product
            else: product_object = Product.objects.get(product_id=item.product_id)
        except Product.DoesNotExist:
            messages.error(request, f"Product ID '{item.product_id}' (from your cart) no longer exists. It has been removed.")
            item.delete(); cart_issues_found = True; continue
        except Exception as e:
            messages.error(request, f"An error occurred with cart item for product ID '{item.product_id}' ({str(e)}). It has been removed.")
            item.delete(); cart_issues_found = True; continue
        
        if product_object.quantity_in_stock == 0:
            messages.warning(request, f"{product_object.product_name} is out of stock and was removed from your cart.")
            item.delete(); cart_issues_found = True; continue
        elif item.quantity > product_object.quantity_in_stock:
            messages.info(request, f"Quantity for {product_object.product_name} was reduced to {product_object.quantity_in_stock} (max available).")
            item.quantity = product_object.quantity_in_stock
            item.save(update_fields=['quantity']); 
        
        valid_items_for_checkout.append({'cart_item': item, 'product_obj': product_object, 'quantity': item.quantity})
        checkout_total_price += product_object.sell_price * item.quantity

    if cart_issues_found and not valid_items_for_checkout: 
        messages.info(request, "Your cart became empty after stock validation. Please add other products.")
        return redirect('products:product_list') # MODIFIED HERE
    elif cart_issues_found: 
         messages.warning(request, "Some items in your cart were adjusted or removed due to availability. Please review the summary before submitting your order.")

    if not valid_items_for_checkout: 
        messages.info(request, "Your cart is empty. Add some products before checking out.")
        return redirect('products:product_list') # MODIFIED HERE

    if request.method == 'POST':
        name = escape(request.POST.get('name', '')).strip()
        address = escape(request.POST.get('address', '')).strip()
        phone = escape(request.POST.get('phone', '')).strip()

        if not all([name, address, phone]):
            messages.error(request, "All fields (name, address, phone) are required for checkout.")
            return render(request, 'checkout.html', {
                'checkout_items': valid_items_for_checkout, 
                'total': checkout_total_price, 
                'form_data': request.POST 
            })

        order = Orders(
            user=request.user.username, customer_name=name, address=address, 
            phone_number=phone, total_price=checkout_total_price, status='Pending' 
        )
        order.save()

        for entry in valid_items_for_checkout:
            OrderDetails.objects.create(
                order_id=order, quantity=entry['quantity'], product_id=entry['product_obj']
            )
            product_to_update = entry['product_obj']
            product_to_update.quantity_in_stock -= entry['quantity']
            product_to_update.save(update_fields=['quantity_in_stock'])

        Cart.objects.filter(user=request.user.username).delete()
        messages.success(request, 'Your order has been placed successfully! Thank you.')
        return redirect('products:orders_get')

    return render(request, 'checkout.html', {
        'checkout_items': valid_items_for_checkout, 
        'total': checkout_total_price
    })

def cart_delete(request, pid):
    if not request.user.is_authenticated: 
        return redirect('login') 
    if request.user.is_superuser: 
        return HttpResponse("Invalid Action for Admin")

    product_instance = get_object_or_404(Product, product_id=pid)
    deleted_count, _ = Cart.objects.filter(user=request.user.username, product=product_instance).delete()

    if deleted_count > 0: 
        messages.info(request, f'{product_instance.product_name} has been removed from your cart.')
    else: 
        messages.warning(request, f'{product_instance.product_name} was not found in your cart.')
    
    return redirect('products:cart_get') 
def order_cancel(request, oid):
    if not request.user.is_authenticated: return redirect('login')
    
    try: order_id_int = int(oid)
    except ValueError:
        messages.error(request, "Invalid order ID format."); return redirect('products:orders_get')

    if request.user.is_superuser:
        messages.error(request, "Admins should use the admin interface to manage orders.")
        return redirect('products:orders_get') 

    order_to_cancel = get_object_or_404(Orders, order_id=order_id_int, user=request.user.username)

    if order_to_cancel.status == 'Pending': 
        order_to_cancel.status = 'Canceled'
        order_to_cancel.save(update_fields=['status'])

        for item_detail in OrderDetails.objects.filter(order_id=order_to_cancel).select_related('product_id'):
            if item_detail.product_id: # Check if product still exists
                product_stock_to_restore = item_detail.product_id
                product_stock_to_restore.quantity_in_stock += item_detail.quantity
                product_stock_to_restore.save(update_fields=['quantity_in_stock'])
        messages.success(request, f"Order #{oid} has been canceled.")
    else:
        messages.error(request, f"Order #{oid} cannot be canceled (status: '{order_to_cancel.status}').")
    return redirect('products:orders_get')

def order_details(request, oid): # This is products.views.order_details
    if not request.user.is_authenticated: return redirect('login')
    
    try: order_id_int = int(oid)
    except ValueError: # Should not happen if URL pattern is <int:oid>
        messages.error(request, "Invalid order ID format."); return redirect('products:orders_get') # Use namespaced redirect

    # If admin, they can see any order. If not admin, they must own the order.
    if request.user.is_superuser:
        order_instance = get_object_or_404(Orders, order_id=order_id_int)
    else:
        order_instance = get_object_or_404(Orders, order_id=order_id_int, user=request.user.username)

    details_for_order = OrderDetails.objects.filter(order_id=order_instance).select_related('product_id')

    # The context key 'order' is used by template order_details.html for order attributes
    return render(request, 'order_details.html', {
        'order': order_instance, 
        'details': details_for_order,
        # 'id', 'status', 'total' are redundant if 'order' object is passed, but kept for safety if template uses them directly
        'id': order_id_int, 
        'status': order_instance.status, 
        'total': order_instance.total_price 
    })