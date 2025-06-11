

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    try:
        import dotenv
    except ImportError:
        pass # dotenv không bắt buộc, nhưng tốt nếu có cho development
    else:
        dotenv.load_dotenv() # Tải các biến từ file .env (nếu tồn tại)
    # ---- KẾT THÚC ĐOẠN THÊM ----
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
