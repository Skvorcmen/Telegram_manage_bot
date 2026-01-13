# render_wsgi.py
import os
import sys

# Абсолютный путь на Render
PROJECT_ROOT = '/opt/render/project/src'

# Добавляем пути
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'config'))

print("=" * 50)
print("Starting Django on Render...")
print(f"Project root: {PROJECT_ROOT}")
print("=" * 50)

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✅ Django application loaded successfully!")
except Exception as e:
    print(f"❌ Error loading Django: {e}")
    import traceback
    traceback.print_exc()
    raise