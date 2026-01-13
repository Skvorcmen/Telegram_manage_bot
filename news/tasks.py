# news/tasks.py
import os
import requests
from django.conf import settings
from django.core.files.storage import default_storage
import tempfile


def publish_to_telegram(post):
    """
    Отправляет новость в Telegram канал.
    Возвращает True при успехе, False при ошибке.
    """
    print(f"📤 DEBUG: Отправка новости в Telegram: '{post.title}'")

    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHANNEL_ID

    if not bot_token:
        print("❌ DEBUG: TELEGRAM_BOT_TOKEN не установлен!")
        print(f"❌ DEBUG: Проверьте переменные окружения на Render")
        return False

    if not chat_id:
        print("❌ DEBUG: TELEGRAM_CHANNEL_ID не установлен!")
        print(f"❌ DEBUG: Проверьте переменные окружения на Render")
        return False

    print(f"🔧 DEBUG: Bot Token (первые 10 символов): {bot_token[:10]}...")
    print(f"🔧 DEBUG: Channel ID: {chat_id}")

    try:
        # Формируем текст сообщения
        message_text = f"<b>{post.title}</b>\n\n{post.content}"

        # Если есть изображение
        if post.image and post.image.name:
            print(f"📷 DEBUG: Отправка изображения: {post.image.name}")
            return send_telegram_photo(bot_token, chat_id, post.image, message_text)

        # Если есть документ
        elif post.document and post.document.name:
            print(f"📎 DEBUG: Отправка документа: {post.document.name}")
            return send_telegram_document(bot_token, chat_id, post.document, message_text)

        # Если только текст
        else:
            print("📝 DEBUG: Отправка только текста")
            return send_telegram_message(bot_token, chat_id, message_text)

    except Exception as e:
        print(f"❌ DEBUG: Ошибка при отправке: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_telegram_message(bot_token, chat_id, text, parse_mode='HTML'):
    """Отправляет текстовое сообщение"""
    try:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }

        print(f"🔧 DEBUG: Отправка текста в Telegram...")
        response = requests.post(url, json=data, timeout=30)
        result = response.json()

        print(f"📡 DEBUG: Ответ Telegram (текст): {result}")

        if result.get('ok'):
            print(f"✅ УСПЕХ: Сообщение отправлено в Telegram")
            return True
        else:
            print(f"❌ ОШИБКА Telegram: {result.get('description')}")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА сети: {str(e)}")
        return False


def send_telegram_photo(bot_token, chat_id, image_field, caption):
    """Отправляет фото с подписью (работает с FileField)"""
    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            # Копируем содержимое файла
            for chunk in image_field.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        print(f"🔧 DEBUG: Временный файл создан: {tmp_path}")

        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'

        with open(tmp_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption[:1024],
                'parse_mode': 'HTML'
            }

            print(f"🔧 DEBUG: Отправка фото в Telegram...")
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()

        # Удаляем временный файл
        os.unlink(tmp_path)

        print(f"📡 DEBUG: Ответ Telegram (фото): {result}")

        if result.get('ok'):
            print(f"✅ УСПЕХ: Фото отправлено в Telegram")
            return True
        else:
            print(f"❌ ОШИБКА Telegram: {result.get('description')}")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА отправки фото: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_telegram_document(bot_token, chat_id, document_field, caption):
    """Отправляет документ с подписью (работает с FileField)"""
    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            # Копируем содержимое файла
            for chunk in document_field.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        print(f"🔧 DEBUG: Временный файл создан: {tmp_path}")
        print(f"🔧 DEBUG: Размер файла: {os.path.getsize(tmp_path)} байт")

        url = f'https://api.telegram.org/bot{bot_token}/sendDocument'

        with open(tmp_path, 'rb') as doc_file:
            filename = os.path.basename(document_field.name)
            files = {'document': (filename, doc_file)}
            data = {
                'chat_id': chat_id,
                'caption': caption[:1024],
                'parse_mode': 'HTML'
            }

            print(f"🔧 DEBUG: Отправка документа в Telegram...")
            response = requests.post(url, files=files, data=data, timeout=60)
            result = response.json()

        # Удаляем временный файл
        os.unlink(tmp_path)

        print(f"📡 DEBUG: Ответ Telegram (документ): {result}")

        if result.get('ok'):
            print(f"✅ УСПЕХ: Документ отправлен в Telegram")
            return True
        else:
            print(f"❌ ОШИБКА Telegram: {result.get('description')}")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА отправки документа: {str(e)}")
        import traceback
        traceback.print_exc()
        return False