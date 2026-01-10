import os
import requests


def publish_to_telegram(news_post):
    """Отправляет новость в Telegram-канал через requests API."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')

    print(f"🔧 Отправка через API: '{news_post.title}'")

    if not bot_token or not channel_id:
        print("❌ Нет токена или ID канала")
        return False

    # Формируем сообщение
    message = f"<b>{news_post.title}</b>\n\n{news_post.content}"

    try:
        # Если есть изображение
        if news_post.image and hasattr(news_post.image, 'path'):
            try:
                url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

                with open(news_post.image.path, 'rb') as photo_file:
                    files = {'photo': photo_file}
                    data = {
                        'chat_id': channel_id,
                        'caption': message,
                        'parse_mode': 'HTML'
                    }

                    response = requests.post(url, files=files, data=data, timeout=30)

            except FileNotFoundError:
                # Если файл не найден - отправляем только текст
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': channel_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, json=data, timeout=30)
        else:
            # Отправка только текста
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
            print(f"   Ответ API: {response.json()}")
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