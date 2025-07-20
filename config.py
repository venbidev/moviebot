import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ID администраторов (список ID пользователей Telegram)
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

# Список каналов для проверки заявок
# Формат: [{"id": channel_id, "title": "Channel Title", "link": "https://t.me/channel"}]
CHANNELS = [
    # Пример:
    {"id": -1001234567890, "title": "[БОЛЬШЕ ФИЛЬМОВ](https://t.me/+RD_RuqQgQYo1ZTNi)", "link": ""},
    # {"id": -1001234567891, "title": "ГОРЯЧИЙ КОНТЕНТ", "link": "https://t.me/hot_content"},
    # {"id": -1001234567892, "title": "НОВОСТИ КРИПТЫ", "link": "https://t.me/crypto_news"},
    # {"id": -1001234567893, "title": "ПСИХОЛОГИЯ", "link": "https://t.me/psychology"},
]

# Путь к базе данных SQLite
DB_PATH = "movie_bot.db"
