# gunicorn.conf.py
import os
import sys

# Критически важно: устанавливаем путь ДО импорта чего-либо
project_root = '/opt/render/project/src'
sys.path.insert(0, project_root)

# Печатаем для отладки
print(f"🔧 Gunicorn config loaded from: {project_root}")
print(f"🔧 Python path: {sys.path}")

# Конфигурация gunicorn
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
worker_class = 'sync'
timeout = 120

# Устанавливаем переменные окружения для ВСЕХ воркеров
raw_env = [
    f'PYTHONPATH={project_root}',
    'DJANGO_SETTINGS_MODULE=config.settings',
]

# Логирование
accesslog = '-'
errorlog = '-'
loglevel = 'debug'