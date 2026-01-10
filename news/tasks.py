import os
import requests
from django.conf import settings


def publish_to_telegram(news_post):
    """Отправляет новость в Telegram-канал через requests API."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')

    print(f"🔧 Отправка: '{news_post.title}' в {channel_id}")

    if not bot_token or not channel_id:
        print("❌ Нет токена или ID канала")
        return False

    # Формируем сообщение
    message = f"<b>{news_post.title}</b>\n\n{news_post.content}"

    try:
        # Ищем файл изображения в разных местах
        image_path = None

        if news_post.image:
            print(f"🖼️ Ищем изображение: {news_post.image.name}")

            # Вариант 1: Прямой путь (если есть)
            if hasattr(news_post.image, 'path') and news_post.image.path:
                if os.path.exists(news_post.image.path):
                    image_path = news_post.image.path
                    print(f"✅ Найден по path: {image_path}")

            # Вариант 2: Через MEDIA_ROOT
            if not image_path and news_post.image.name:
                possible_path = os.path.join(settings.MEDIA_ROOT, news_post.image.name)
                if os.path.exists(possible_path):
                    image_path = possible_path
                    print(f"✅ Найден в MEDIA_ROOT: {image_path}")

            # Вариант 3: Относительный путь
            if not image_path and news_post.image.name:
                possible_path = os.path.join('media', news_post.image.name)
                if os.path.exists(possible_path):
                    image_path = possible_path
                    print(f"✅ Найден по относительному пути: {image_path}")

            if image_path:
                print(f"📏 Размер файла: {os.path.getsize(image_path) / 1024:.1f} KB")

        # Если нашли изображение - отправляем с фото
        if image_path and os.path.exists(image_path):
            print(f"📤 Отправляем с фото: {image_path}")

            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

            with open(image_path, 'rb') as photo_file:
                files = {
                    'photo': (os.path.basename(image_path), photo_file)
                }

                data = {
                    'chat_id': channel_id,
                    'caption': message,
                    'parse_mode': 'HTML'
                }

                response = requests.post(url, files=files, data=data, timeout=30)
        else:
            print("📝 Изображение не найдено, отправляем только текст")
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': channel_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=data, timeout=30)

        # Проверяем результат
        if response.status_code == 200:
            print(f"✅ УСПЕХ: Новость '{news_post.title}' отправлена!")
            return True
        else:
            print(f"❌ ОШИБКА API: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False