# tasks.py
import os
import requests
from django.conf import settings
from django.core.files.storage import default_storage


def publish_to_telegram(post):
    """
    Отправляет новость в Telegram канал.
    Возвращает True при успехе, False при ошибке.
    """
    print(f"📤 DEBUG: Отправка новости в Telegram: '{post.title}'")

    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHANNEL_ID

    if not bot_token or not chat_id:
        print("❌ DEBUG: Токен бота или ID канала не настроены")
        return False

    try:
        # Формируем текст сообщения
        message_text = f"<b>{post.title}</b>\n\n{post.content}"

        # Если есть изображение
        if post.image:
            print(f"📷 DEBUG: Отправка изображения: {post.image.name}")
            return send_photo_with_caption(
                bot_token,
                chat_id,
                post.image.path,
                message_text
            )

        # Если есть документ
        elif post.document:
            print(f"📎 DEBUG: Отправка документа: {post.document.name}")
            return send_document_with_caption(
                bot_token,
                chat_id,
                post.document.path,
                message_text
            )

        # Если только текст
        else:
            print("📝 DEBUG: Отправка только текста")
            return send_text_message(
                bot_token,
                chat_id,
                message_text
            )

    except Exception as e:
        print(f"❌ DEBUG: Ошибка при отправке: {str(e)}")
        return False


def send_text_message(bot_token, chat_id, text, parse_mode='HTML'):
    """Отправляет текстовое сообщение"""
    try:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }

        response = requests.post(url, json=data, timeout=30)
        result = response.json()

        print(f"📡 DEBUG: Ответ Telegram (текст): {result}")
        return result.get('ok', False)

    except Exception as e:
        print(f"❌ DEBUG: Ошибка отправки текста: {str(e)}")
        return False


def send_photo_with_caption(bot_token, chat_id, image_path, caption):
    """Отправляет фото с подписью"""
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            print(f"❌ DEBUG: Файл изображения не найден: {image_path}")
            return False

        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'

        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption[:1024],  # Ограничение Telegram
                'parse_mode': 'HTML'
            }

            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()

            print(f"📡 DEBUG: Ответ Telegram (фото): {result}")
            return result.get('ok', False)

    except Exception as e:
        print(f"❌ DEBUG: Ошибка отправки фото: {str(e)}")
        return False


def send_document_with_caption(bot_token, chat_id, document_path, caption):
    """Отправляет документ с подписью"""
    print(f"🔍 DEBUG: Путь к документу: {document_path}")
    print(f"🔍 DEBUG: Файл существует: {os.path.exists(document_path)}")

    try:
        # Проверяем существование файла
        if not os.path.exists(document_path):
            print(f"❌ DEBUG: Файл документа не найден: {document_path}")
            # Пробуем альтернативный путь через MEDIA_ROOT
            alt_path = os.path.join(settings.MEDIA_ROOT, document_path)
            if os.path.exists(alt_path):
                document_path = alt_path
                print(f"✅ DEBUG: Найден альтернативный путь: {document_path}")
            else:
                return False

        # Проверяем размер файла
        file_size = os.path.getsize(document_path)
        print(f"📊 DEBUG: Размер файла: {file_size} байт ({file_size / 1024 / 1024:.2f} MB)")

        # Telegram ограничение: 50 MB для документов
        if file_size > 50 * 1024 * 1024:
            print(f"❌ DEBUG: Файл слишком большой: {file_size / 1024 / 1024:.2f} MB")
            return False

        url = f'https://api.telegram.org/bot{bot_token}/sendDocument'

        with open(document_path, 'rb') as document_file:
            # Получаем имя файла
            filename = os.path.basename(document_path)

            # Важно: передаем кортеж (имя_файла, файл, mime_type)
            files = {
                'document': (filename, document_file)
            }

            data = {
                'chat_id': chat_id,
                'caption': caption[:1024],  # Ограничение Telegram
                'parse_mode': 'HTML'
            }

            print(f"📤 DEBUG: Отправка документа {filename} в Telegram...")
            response = requests.post(url, files=files, data=data, timeout=60)
            result = response.json()

            print(f"📡 DEBUG: Полный ответ Telegram: {result}")

            if result.get('ok'):
                print(f"✅ DEBUG: Документ успешно отправлен")
                return True
            else:
                print(f"❌ DEBUG: Ошибка Telegram API: {result.get('description')}")
                return False

    except FileNotFoundError as e:
        print(f"❌ DEBUG: Файл не найден: {str(e)}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ DEBUG: Ошибка сети: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ DEBUG: Неожиданная ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return False