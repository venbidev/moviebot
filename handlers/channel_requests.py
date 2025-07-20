from aiogram import Router, F
from aiogram.types import ChatJoinRequest
from database import DatabaseManager
from config import DB_PATH, CHANNELS

# Инициализация менеджера базы данных
db = DatabaseManager(DB_PATH)

# Создание роутера для обработки заявок в каналы
router = Router()

@router.chat_join_request()
async def process_join_request(join_request: ChatJoinRequest):
    """
    Обработчик заявок на вступление в канал.
    Сохраняет информацию о заявке в базу данных.
    """
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id
    
    # Проверяем, является ли канал одним из наших каналов
    is_our_channel = False
    for channel in CHANNELS:
        if channel["id"] == chat_id:
            is_our_channel = True
            break
    
    if is_our_channel:
        # Сохраняем информацию о заявке в базу данных
        db.add_channel_request(user_id, chat_id, status="pending")
        
        # Автоматически одобряем заявку
        try:
            await join_request.approve()
            # Обновляем статус заявки в базе данных
            db.update_channel_request_status(user_id, chat_id, status="approved")
        except Exception as e:
            print(f"Error approving join request: {e}")
