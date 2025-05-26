# admin/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.utils.html import escape # Added back for order_filter example (though this view is redundant)

from products.models import Product, Orders, OrderDetails 
from products.forms import ProductForm 
from django.core.paginator import Paginator


# Admin's product functions
def product_change(request, pid): 
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page")
        return redirect('products:product_list') # Redirect to a general page
    
    product_instance = get_object_or_404(Product, product_id=pid) 

    if request.method == 'POST':
        # Pass is_edit=True to the form constructor
        form = ProductForm(request.POST, request.FILES, instance=product_instance, is_edit=True)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin: Product updated successfully!")
            # Using namespaced URL for product list
            return redirect('products:product_list') 
    else:
        # Pass is_edit=True to the form constructor
        form = ProductForm(instance=product_instance, is_edit=True) 

    context = {
        'form': form,
        'product': product_instance,
        'is_edit': True,
        # The form action should ideally use reverse if admin URLs are namespaced, e.g., reverse('admin:product_accept_change', args=[pid])
        # For now, keeping the hardcoded admin path as per existing structure.
        'url': f"/admin/products/accept_change/{pid}" 
    }
    return render(request, 'products/product_add.html', context)


def product_add(request): # admin.views.product_add
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('products:product_list') 

    # Action URL for the form. If admin URLs get a namespace 'admin', this would be reverse('admin:product_accept_add')
    form_action_url = "/admin/products/accept_add/" 

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) # is_edit is False by default in ProductForm
        if form.is_valid():
            form.save()
            messages.success(request, "Admin: Product added successfully!")
            return redirect('products:product_list') # Redirect to general product list
    else:
        form = ProductForm() # is_edit is False by default

    context = {
        'form': form,      
        'product': None,   
        'is_edit': False,  
        'url': form_action_url
    }
    return render(request, 'products/product_add.html', context)

def product_accept_change(request, pid): # admin.views.product_accept_change
    if not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền truy cập trang này")
        return redirect('products:product_list')
    
    product_instance = get_object_or_404(Product, product_id=pid) 
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product_instance, is_edit=True) 
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật sản phẩm thành công!")
            return redirect('products:product_list') # MODIFIED HERE
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin nhập.")
            context = {
                'form': form,
                'product': product_instance,
                'is_edit': True,
                'url': f"/admin/products/accept_change/{pid}"
            }
            return render(request, 'products/product_add.html', context) 
    # If GET, redirect to the change form. Use reverse if admin URLs are namespaced.
    return redirect(f'/admin/products/change/{pid}/') 


def product_accept_add(request): # admin.views.product_accept_add
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page")
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm sản phẩm thành công!")
            return redirect('products:product_list') # MODIFIED HERE
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin nhập.")
            context = {
                'form': form,
                'product': None,
                'is_edit': False,
                'url': "/admin/products/accept_add/"
            }
            return render(request, 'products/product_add.html', context) 

    # If GET, redirect to the add form. Use reverse if admin URLs are namespaced.
    return redirect('/admin/products/add/') 


def product_delete(request, pid): # admin.views.product_delete
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page")
        return redirect('products:product_list')
        
    product_instance = get_object_or_404(Product, product_id=pid) 
    product_name = product_instance.product_name
    product_instance.delete()
    messages.success(request, f"Sản phẩm {product_name} đã được xóa.")
    return redirect('products:product_list') # MODIFIED HERE

def order_status_change(request, oid, action): # SỬA ĐỔI Ở ĐÂY: Thêm tham số action, oid là int
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('products:orders_get') # Chuyển hướng về danh sách đơn hàng chung
            
    order = get_object_or_404(Orders, order_id=oid)
    original_status = order.status
    action_performed = False

    if action == 'confirm' and order.status == Orders.ORDER_STATUS_CHOICES[0][0]: # Pending
        order.status = Orders.ORDER_STATUS_CHOICES[1][0] # Confirmed
        messages.success(request, f"Order #{oid} status changed to Confirmed.")
        action_performed = True
    elif action == 'process' and order.status == Orders.ORDER_STATUS_CHOICES[1][0]: # Confirmed
        order.status = Orders.ORDER_STATUS_CHOICES[2][0] # Processing
        messages.success(request, f"Order #{oid} status changed to Processing.")
        action_performed = True
    elif action == 'ship' and order.status == Orders.ORDER_STATUS_CHOICES[2][0]: # Processing
        order.status = Orders.ORDER_STATUS_CHOICES[3][0] # Shipped
        messages.success(request, f"Order #{oid} status changed to Shipped.")
        action_performed = True
    elif action == 'deliver' and order.status == Orders.ORDER_STATUS_CHOICES[3][0]: # Shipped
        order.status = Orders.ORDER_STATUS_CHOICES[4][0] # Delivered
        messages.success(request, f"Order #{oid} status changed to Delivered.")
        action_performed = True
    elif action == 'cancel':
        # Admin có thể hủy đơn ở các trạng thái cho phép (ví dụ: Pending, Confirmed, Processing)
        allowed_cancel_statuses = [
            Orders.ORDER_STATUS_CHOICES[0][0], # Pending
            Orders.ORDER_STATUS_CHOICES[1][0], # Confirmed
            Orders.ORDER_STATUS_CHOICES[2][0]  # Processing
        ]
        if order.status in allowed_cancel_statuses:
            order.status = Orders.ORDER_STATUS_CHOICES[5][0] # Canceled
            
            # Hoàn kho khi admin hủy đơn
            for item_detail in OrderDetails.objects.filter(order_id=order).select_related('product_id'):
                if item_detail.product_id: # Kiểm tra sản phẩm còn tồn tại không
                    product_stock_to_restore = item_detail.product_id
                    product_stock_to_restore.quantity_in_stock += item_detail.quantity
                    product_stock_to_restore.save(update_fields=['quantity_in_stock'])
            
            messages.success(request, f"Order #{oid} has been canceled by admin. Stock restored.")
            action_performed = True
        else:
            messages.error(request, f"Order #{oid} (Status: {order.status}) cannot be canceled by admin at this stage.")
    else:
        messages.info(request, f"Invalid action '{action}' or order #{oid} status ('{order.status}') not eligible for this action.")
    
    if action_performed and order.status != original_status: 
        order.save(update_fields=["status"])
    
    # Chuyển hướng về trang chi tiết của đơn hàng đó hoặc danh sách đơn hàng
    # Nếu bạn có URL admin_order_details, hãy dùng nó. Nếu không, dùng products:order_details
    return redirect('products:order_details', oid=oid)

def order_filter(request): # admin.views.order_filter (This view is mostly redundant with products.views.orders_get)
    if not request.user.is_superuser: # Should be specific to admin
        messages.error(request, "Access denied.")
        return redirect('products:product_list') # Or login

    order_query = Orders.objects.all() # Admin sees all orders

    status_filter_from_url = request.GET.get("status", "").strip()
    
    if status_filter_from_url:
        model_status_filter = None
        for val, display_name in Orders.ORDER_STATUS_CHOICES:
            if status_filter_from_url == val.lower():
                model_status_filter = val
                break
        if model_status_filter:
            order_query = order_query.filter(status=model_status_filter)
    
    order_query = order_query.order_by('-order_id')
            
    context = {
        'orders': order_query,
        'user_order_status_choices': Orders.ORDER_STATUS_CHOICES # For filter dropdown in order.html
    }
    # This renders 'order.html' which is likely products/order.html.
    # Ensure this template can handle both admin and user views or use a separate admin_order_list.html.
    return render(request, 'order.html', context)


def order_details(request, oid): # admin.views.order_details
    order_instance = get_object_or_404(Orders, order_id=oid)
    
    if not request.user.is_superuser:
        # Non-admins should not use this admin view for order details.
        # They should be directed to products.views.order_details which checks ownership.
        messages.error(request, "Access denied to admin order details.")
        return redirect('products:orders_get') 

    details_for_order = OrderDetails.objects.filter(order_id=order_instance).select_related('product_id')

    context = {
        'order': order_instance, 
        'details': details_for_order,
        # Redundant if 'order' is passed and template uses order.xyz
        'id': order_instance.order_id, 
        'status': order_instance.status, 
        'total': order_instance.total_price 
    }
    # This renders 'order_details.html' which is likely products/order_details.html.
    return render(request, 'order_details.html', context)

# This product_list in admin/views.py is a duplicate of products.views.product_list
# It's generally better to avoid such duplication. If admin needs a different list,
# it should be a distinct view or the main one should be adaptable.
# For now, assuming products.views.product_list is the main one.
# If this view is actually used by an admin-specific URL, that URL should call this view.
# And its redirect should also be namespaced if needed.
def product_list(request): # admin.views.product_list
    # If this is an admin-specific product list, it might have different filters or fields.
    # For now, it's a copy of the public one.
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
    else: 
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
    # Renders products/product.html. If admin URL calls this, this is the template used.
    return render(request, 'products/product.html', context)