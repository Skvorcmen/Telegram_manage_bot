# start.py
import os
import sys
import subprocess


def main():
    print("🚀 Starting Django on Render...")

    # Устанавливаем пути
    project_root = '/opt/render/project/src'
    sys.path.insert(0, project_root)

    # Выполняем миграции
    print("📦 Running migrations...")
    try:
        subprocess.run([
            sys.executable, 'config/manage.py', 'migrate', '--noinput'
        ], cwd=project_root, check=True)
        print("✅ Migrations completed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Migrations failed: {e}")

    # Создаем суперпользователя
    print("👤 Creating superuser...")
    try:
        subprocess.run([
            sys.executable, '-c', """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin created')
else:
    print('Admin already exists')
"""
        ], cwd=project_root, check=True)
        print("✅ Superuser check completed")
    except:
        print("⚠️ Superuser creation skipped")

    # Запускаем gunicorn
    print("🚀 Starting Gunicorn...")
    os.execl(
        sys.executable,
        sys.executable,
        '-m', 'gunicorn',
        'config.wsgi:application',
        '-c', 'gunicorn.conf.py'
    )


if __name__ == '__main__':
    main()