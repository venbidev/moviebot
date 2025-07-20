import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, ADMIN_IDS
from handlers import user_router, admin_router, channel_requests_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Список команд бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="admin", description="Админ-панель (только для администраторов)")
    ]
    await bot.set_my_commands(commands)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(channel_requests_router)
    
    # Установка команд бота
    await set_commands(bot)
    
    # Вывод информации о запуске бота
    logging.info("Бот запущен")
    
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
