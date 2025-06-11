import os
from dotenv import load_dotenv # Import thư viện

# Xác định BASE_DIR (thư mục gốc của dự án)
# Cách này thường dùng nếu settings.py nằm trong một thư mục con (ví dụ: 'shop')
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Hoặc nếu settings.py nằm ngay thư mục gốc, thì:
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Hãy đảm bảo BASE_DIR trỏ đúng đến thư mục chứa file .env của bạn.
# Cách phổ biến cho cấu trúc dự án Django hiện đại:
# (Giả sử settings.py nằm trong shop/shop/settings.py và .env nằm ở shop/)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent # Trỏ lên 2 cấp để ra thư mục gốc dự án

# Tải các biến từ file .env vào biến môi trường của OS
# load_dotenv() sẽ tự động tìm file .env ở thư mục hiện tại hoặc các thư mục cha
# Hoặc bạn có thể chỉ định đường dẫn rõ ràng:
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"CẢNH BÁO: File .env không tìm thấy tại {dotenv_path}. Các biến môi trường có thể không được tải đúng cách.")


# Đọc các khóa PayOS từ biến môi trường (đã được load_dotenv nạp vào)
PAYOS_CLIENT_ID = os.environ.get('PAYOS_CLIENT_ID')
PAYOS_API_KEY = os.environ.get('PAYOS_API_KEY')
PAYOS_CHECKSUM_KEY = os.environ.get('PAYOS_CHECKSUM_KEY')

# Kiểm tra xem các key có được tải không (quan trọng cho debug)
if not PAYOS_CLIENT_ID:
    print("CẢNH BÁO: PAYOS_CLIENT_ID không được tìm thấy trong biến môi trường.")
if not PAYOS_API_KEY:
    print("CẢNH BÁO: PAYOS_API_KEY không được tìm thấy trong biến môi trường.")
if not PAYOS_CHECKSUM_KEY:
    print("CẢNH BÁO: PAYOS_CHECKSUM_KEY không được tìm thấy trong biến môi trường.")
SECRET_KEY = '&5c1wcgzgoighiw1js%$n8otv!_e&1gm*j(dfxzgcp65fttxv2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'web-b-n-8trv.onrender.com',
    'localhost',
    '127.0.0.1',

    # Hoặc nếu bạn muốn cho phép tất cả các subdomain của ngrok-free.app (nếu sau này URL thay đổi):
    # '.ngrok-free.app',
]


# Application definition

INSTALLED_APPS = [
    'mainpage.apps.MainpageConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mathfilters',
    'products',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # Thêm media context processor
            ],
        },
    },
]

WSGI_APPLICATION = 'shop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shopdb',
        'USER': 'postgres',
        'PASSWORD': '28072004',
        'HOST': 'localhost',  # Hoặc địa chỉ máy chủ PostgreSQL
        'PORT': '5432',  # Cổng mặc định PostgreSQL
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static/staticfiles"),
    os.path.join(BASE_DIR,"accounts/static")
]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
from decouple import config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # hoặc SMTP server của bạn
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'doanduychien204@gmail.com'
EMAIL_HOST_PASSWORD = 'hwor lyat ygbw xmld' # Nhập app password của email
DEFAULT_FROM_EMAIL = 'doanduychien204@gmail.com'
