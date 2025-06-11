# shop/settings.py

import os
import dj_database_url
from pathlib import Path

# --- CẤU TRÚC THƯ MỤC ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- QUAN TRỌNG: CẤU HÌNH BIẾN MÔI TRƯỜNG ---
# Trên Render, bạn sẽ KHÔNG dùng file .env. Thay vào đó, bạn sẽ thêm các biến này
# vào tab "Environment" trong dashboard của dịch vụ.
# Đoạn code dưới đây chỉ để tiện phát triển ở máy local.
from dotenv import load_dotenv
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# --- CÁC THIẾT LẬP BẢO MẬT VÀ PRODUCTION ---

# Lấy SECRET_KEY từ biến môi trường. KHÔNG BAO GIỜ hardcode nó.
SECRET_KEY = os.environ.get('SECRET_KEY')

# DEBUG = False trên production. 
# Chúng ta sẽ đọc giá trị từ biến môi trường. Mặc định là False.
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Cấu hình ALLOWED_HOSTS cho cả local và Render
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

# Tự động thêm domain của Render vào ALLOWED_HOSTS nếu nó tồn tại
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    'mainpage.apps.MainpageConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Thêm WhiteNoise vào đây
    'whitenoise.runserver_nostatic', 
    'django.contrib.staticfiles',
    'mathfilters',
    'products',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Thêm WhiteNoise Middleware ngay sau SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'shop.wsgi.application'

# --- DATABASE ---
# Cấu hình database để đọc từ biến môi trường DATABASE_URL mà Render cung cấp.
DATABASES = {
    'default': dj_database_url.config(
        # Fallback về database local nếu không tìm thấy DATABASE_URL
        default=f'postgresql://postgres:28072004@localhost:5432/shopdb',
        conn_max_age=600
    )
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True # Nên đặt là True cho production

# --- STATIC FILES (CSS, JavaScript, Images) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CÁC BIẾN CỦA BẠN (PayOS, Email) ---
# Đọc từ biến môi trường
PAYOS_CLIENT_ID = os.environ.get('PAYOS_CLIENT_ID')
PAYOS_API_KEY = os.environ.get('PAYOS_API_KEY')
PAYOS_CHECKSUM_KEY = os.environ.get('PAYOS_CHECKSUM_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER