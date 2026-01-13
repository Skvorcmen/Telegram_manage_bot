from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Test Telegram connection'

    def handle(self, *args, **kwargs):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        channel_id = settings.TELEGRAM_CHANNEL_ID

        self.stdout.write(f"Bot Token: {'✅ SET' if bot_token else '❌ NOT SET'}")
        self.stdout.write(f"Channel ID: {'✅ SET' if channel_id else '❌ NOT SET'}")

        if bot_token:
            # Test bot
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.stdout.write("✅ Bot is active")
                    self.stdout.write(f"Bot info: {response.json()}")
                else:
                    self.stdout.write(f"❌ Bot error: {response.text}")
            except Exception as e:
                self.stdout.write(f"❌ Network error: {e}")