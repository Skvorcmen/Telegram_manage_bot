import os
import requests
from django.conf import settings


def publish_to_telegram(news_post):
    """Отправляет новость в Telegram-канал."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')

    print(f"🔧 Отправка: '{news_post.title}'")
    print(f"📝 Комментарий (не отправляется): {news_post.comment[:50] if news_post.comment else 'Нет'}")

    if not bot_token or not channel_id:
        print("❌ Нет токена или ID канала")
        return False

    # Формируем сообщение
    message = f"<b>{news_post.title}</b>\n\n{news_post.content}"

    try:
        # 1. Если есть видео файл
        if news_post.video and hasattr(news_post.video, 'path'):
            video_path = find_file_path(news_post.video)
            if video_path:
                print(f"🎬 Отправляем видео файл: {video_path}")
                return send_video(bot_token, channel_id, video_path, message)

        # 2. Если есть ссылка на видео (YouTube/Vimeo)
        elif news_post.video_url:
            print(f"🔗 Отправляем ссылку на видео: {news_post.video_url}")
            # Добавляем ссылку в сообщение
            message += f"\n\n🎥 Видео: {news_post.video_url}"
            return send_message(bot_token, channel_id, message)

        # 3. Если есть изображение
        elif news_post.image and hasattr(news_post.image, 'path'):
            image_path = find_file_path(news_post.image)
            if image_path:
                print(f"📸 Отправляем изображение: {image_path}")
                return send_photo(bot_token, channel_id, image_path, message)

        # 4. Только текст
        else:
            print(f"📝 Отправляем только текст")
            return send_message(bot_token, channel_id, message)

    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def find_file_path(file_field):
    """Находит путь к файлу в разных местах."""
    if not file_field:
        return None

    # Вариант 1: Прямой путь
    if hasattr(file_field, 'path') and file_field.path:
        if os.path.exists(file_field.path):
            return file_field.path

    # Вариант 2: Через MEDIA_ROOT
    if file_field.name:
        possible_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
        if os.path.exists(possible_path):
            return possible_path

    # Вариант 3: Относительный путь
    if file_field.name:
        possible_path = os.path.join('media', file_field.name)
        if os.path.exists(possible_path):
            return possible_path

    return None


def send_video(bot_token, channel_id, video_path, message):
    """Отправляет видео в Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"

        # Проверяем размер файла (Telegram лимит: 50MB для ботов)
        file_size = os.path.getsize(video_path)
        max_size = 50 * 1024 * 1024  # 50MB

        if file_size > max_size:
            print(f"⚠️ Видео слишком большое ({file_size / 1024 / 1024:.1f}MB > 50MB)")
            print(f"📝 Отправляем только описание с ссылкой")
            message += f"\n\n⚠️ Видео слишком большое для отправки"
            return send_message(bot_token, channel_id, message)

        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {
                'chat_id': channel_id,
                'caption': message[:1024],  # Ограничение для подписи
                'parse_mode': 'HTML',
                'supports_streaming': True  # Для потокового воспроизведения
            }

            response = requests.post(url, files=files, data=data, timeout=60)

            if response.status_code == 200:
                print(f"✅ Видео отправлено!")
                return True
            else:
                print(f"❌ Ошибка отправки видео: {response.text}")
                # Пробуем отправить как документ
                return send_document(bot_token, channel_id, video_path, message)

    except Exception as e:
        print(f"❌ Ошибка при отправке видео: {e}")
        return send_message(bot_token, channel_id, message)


def send_photo(bot_token, channel_id, image_path, message):
    """Отправляет фото в Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

        with open(image_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            data = {
                'chat_id': channel_id,
                'caption': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, files=files, data=data, timeout=30)

            if response.status_code == 200:
                print(f"✅ Фото отправлено!")
                return True
            else:
                print(f"❌ Ошибка отправки фото: {response.text}")
                return send_message(bot_token, channel_id, message)

    except Exception as e:
        print(f"❌ Ошибка при отправке фото: {e}")
        return send_message(bot_token, channel_id, message)


def send_document(bot_token, channel_id, file_path, message):
    """Отправляет файл как документ (запасной вариант)."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {
                'chat_id': channel_id,
                'caption': message[:200],
                'parse_mode': 'HTML'
            }

            response = requests.post(url, files=files, data=data, timeout=60)

            if response.status_code == 200:
                print(f"✅ Документ отправлен!")
                return True
            else:
                print(f"❌ Ошибка отправки документа: {response.text}")
                return send_message(bot_token, channel_id, message)

    except Exception as e:
        print(f"❌ Ошибка в send_document: {e}")
        return send_message(bot_token, channel_id, message)


def send_message(bot_token, channel_id, message):
    """Отправляет только текстовое сообщение."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': channel_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False  # Показывать превью ссылок
        }

        response = requests.post(url, json=data, timeout=30)

        if response.status_code == 200:
            print(f"✅ Сообщение отправлено!")
            return True
        else:
            print(f"❌ Ошибка отправки сообщения: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Ошибка в send_message: {e}")
        return False