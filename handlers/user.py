from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_start_keyboard
from database import DatabaseManager
from config import DB_PATH, CHANNELS

# Инициализация менеджера базы данных
db = DatabaseManager(DB_PATH)

# Создание роутера для пользовательских команд
router = Router()

# Определение состояний для FSM (Finite State Machine)
class UserStates(StatesGroup):
    waiting_for_code = State()  # Ожидание ввода кода фильма

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Сохраняем или обновляем информацию о пользователе
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    db.add_or_update_user(user_id, username, first_name, last_name)
    
    # Сбрасываем состояние FSM
    await state.clear()
    
    # Отправляем приветственное сообщение
    await message.answer(
        "Привет! Для поиска фильма нажимай кнопку «Ввести код». Фильмы пополняются ежедневно.\n\n"
        "Спасибо за выбор нашего кинобота!",
        reply_markup=get_start_keyboard()
    )

# Обработчик нажатия на кнопку "Ввести код"
@router.message(F.text == "Ввести код")
async def enter_code_button(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Увеличиваем счетчик кликов и получаем новое значение
    click_count = db.increment_click_count(user_id)
    
    if click_count >= 3:
        # Если пользователь нажал на кнопку 3 или более раз, разрешаем ввод кода
        await state.set_state(UserStates.waiting_for_code)
        await message.answer("Введите код фильма:")
        
        # Сбрасываем счетчик кликов
        db.reset_click_count(user_id)
    else:
        # Если пользователь нажал на кнопку меньше 3 раз
        remaining_clicks = 3 - click_count
        
        # Формируем сообщение с ссылками на каналы из config.py
        channels_text = "Для пользования ботом нужно обязательно подписаться на каналы команды!\n\n"
        
        for channel in CHANNELS:
            # Добавляем название канала как ссылку
            channels_text += f"<a href='{channel['link']}'>{channel['title']}</a>\n"
        
        channels_text += "\nБлагодарим за поддержку!\n\n"
        
        await message.answer(
            channels_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

# Обработчик ввода кода фильма
@router.message(StateFilter(UserStates.waiting_for_code))
async def process_movie_code(message: Message, state: FSMContext):
    code = message.text.strip()
    
    # Ищем фильм по коду
    movie = db.get_movie_by_code(code)
    
    if movie:
        # Если фильм найден, отправляем его название
        await message.answer(f"Название фильма: {movie['title']}")
        
        # Увеличиваем счетчик использования кода
        db.increment_movie_usage(code)
    else:
        # Если фильм не найден
        await message.answer("Фильм с таким кодом не найден. Пожалуйста, проверьте код и попробуйте снова.")
    
    # Сбрасываем состояние
    await state.clear()
