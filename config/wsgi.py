# wsgi.py в КОРНЕ проекта
import os
import sys

# Добавляем пути
current_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(current_dir, 'config')

sys.path.insert(0, current_dir)
sys.path.insert(0, config_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    print(f"Error: {e}")
    raise