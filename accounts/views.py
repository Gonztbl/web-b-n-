from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

# View đăng ký
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Kiểm tra mật khẩu có khớp không
        if password != password2:
            messages.error(request, "Mật khẩu không trùng khớp!")
            return render(request, 'register.html', {'username': username, 'email': email})

        # Kiểm tra xem username đã tồn tại chưa
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username đã tồn tại!")
            return render(request, 'register.html', {'username': username, 'email': email})

        # Kiểm tra xem email đã tồn tại chưa
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng!")
            return render(request, 'register.html', {'username': username, 'email': email})

        # Kiểm tra email hợp lệ
        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, "Email không hợp lệ!")
            return render(request, 'register.html', {'username': username, 'email': email})

        # Kiểm tra mật khẩu hợp lệ
        try:
            validate_password(password)
        except ValidationError as e:
            # Lấy các lỗi mật khẩu và hiển thị cho người dùng
            for err in e.messages:
                messages.error(request, err)
            return render(request, 'register.html', {'username': username, 'email': email})

        # Tạo tài khoản người dùng mới
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
            return redirect('login')
        except Exception as e:
            print("ĐĂNG KÝ LỖI:", e)  # In ra terminal
            messages.error(request, f"Đăng ký không thành công. {str(e)}")
            return redirect('register')

    return render(request, 'register.html')

# View đăng nhập
def login(request):
    if request.method == 'POST':  # Kiểm tra phương thức HTTP là POST không
        form = AuthenticationForm(request, data=request.POST)  # Tạo form từ dữ liệu POST
        if form.is_valid():  # Kiểm tra xem form có hợp lệ không
            auth_login(request, form.get_user())  # Đăng nhập người dùng
            messages.success(request, "Đăng nhập thành công.")  # Thông báo thành công
            return redirect('home')  # Chuyển hướng về trang chủ sau khi đăng nhập
        else:
            messages.error(request, "Đăng nhập không thành công. Vui lòng kiểm tra lại.")  # Thông báo lỗi
    else:
        form = AuthenticationForm()  # Nếu là GET request, tạo form đăng nhập rỗng

    return render(request, 'login.html', {'form': form})  # Render form đăng nhập

# View đăng xuất
def logout(request):
    auth_logout(request)  # Đăng xuất người dùng
    messages.success(request, "Bạn đã đăng xuất thành công.")  # Thông báo thành công
    return redirect('home')  # Chuyển hướng về trang chủ sau khi đăng xuất
