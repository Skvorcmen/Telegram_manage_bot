# wsgi.py в КОРНЕ проекта
import os
import sys

# Получаем абсолютный путь к корню проекта
current_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем корень проекта в sys.path
sys.path.insert(0, current_dir)

# Добавляем путь к папке config
config_dir = os.path.join(current_dir, 'config')
sys.path.insert(0, config_dir)

print(f"✅ Current directory: {current_dir}")
print(f"✅ Config directory: {config_dir}")
print(f"✅ Python path: {sys.path}")

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✅ Django WSGI application loaded successfully")
except Exception as e:
    print(f"❌ Error loading Django: {e}")
    raise