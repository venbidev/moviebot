from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_admin_keyboard, get_start_keyboard
from database import DatabaseManager
from config import DB_PATH, ADMIN_IDS

# Инициализация менеджера базы данных
db = DatabaseManager(DB_PATH)

# Создание роутера для админских команд
router = Router()

# Определение состояний для FSM (Finite State Machine)
class AdminStates(StatesGroup):
    in_admin_panel = State()  # В админ-панели
    adding_movie = State()    # Добавление фильма - ожидание кода
    adding_movie_title = State()  # Добавление фильма - ожидание названия
    deleting_movie = State()  # Удаление фильма
    broadcasting = State()    # Рассылка сообщения

# Middleware для проверки прав администратора
@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if user_id in ADMIN_IDS:
        # Устанавливаем состояние админ-панели
        await state.set_state(AdminStates.in_admin_panel)
        
        # Отправляем сообщение с админ-клавиатурой
        await message.answer(
            "Вы вошли в админ-панель. Выберите действие:",
            reply_markup=get_admin_keyboard()
        )
    else:
        # Если пользователь не админ, отправляем сообщение об ошибке
        await message.answer("У вас нет прав для доступа к админ-панели.")

# Обработчик выхода из админ-панели
@router.message(StateFilter(AdminStates.in_admin_panel), F.text == "Выйти из админ-панели")
async def exit_admin_panel(message: Message, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    
    # Отправляем сообщение о выходе
    await message.answer(
        "Вы вышли из админ-панели.",
        reply_markup=get_start_keyboard()
    )

# Обработчик кнопки "Добавить фильм"
@router.message(StateFilter(AdminStates.in_admin_panel), F.text == "Добавить фильм")
async def add_movie_start(message: Message, state: FSMContext):
    # Устанавливаем состояние добавления фильма
    await state.set_state(AdminStates.adding_movie)
    
    # Запрашиваем код фильма
    await message.answer("Введите код фильма:")

# Обработчик ввода кода фильма
@router.message(StateFilter(AdminStates.adding_movie))
async def add_movie_code(message: Message, state: FSMContext):
    # Получаем код фильма
    code = message.text.strip()
    
    # Проверяем, существует ли фильм с таким кодом
    existing_movie = db.get_movie_by_code(code)
    
    if existing_movie:
        # Если фильм с таким кодом уже существует
        await message.answer(
            f"Фильм с кодом '{code}' уже существует: {existing_movie['title']}.\n"
            f"Использований: {existing_movie['usage_count']}\n"
            "Пожалуйста, введите другой код или вернитесь в админ-панель.",
            reply_markup=get_admin_keyboard()
        )
        await state.set_state(AdminStates.in_admin_panel)
    else:
        # Если код уникален, сохраняем его и запрашиваем название
        await state.update_data(code=code)
        await state.set_state(AdminStates.adding_movie_title)
        await message.answer("Введите название фильма:")

# Обработчик ввода названия фильма
@router.message(StateFilter(AdminStates.adding_movie_title))
async def add_movie_title(message: Message, state: FSMContext):
    # Получаем название фильма
    title = message.text.strip()
    
    # Получаем сохраненный код
    data = await state.get_data()
    code = data.get("code")
    
    # Добавляем фильм в базу данных
    success = db.add_movie(code, title)
    
    if success:
        # Если фильм успешно добавлен
        await message.answer(
            f"Фильм успешно добавлен:\nКод: {code}\nНазвание: {title}\nИспользований: 0",
            reply_markup=get_admin_keyboard()
        )
    else:
        # Если произошла ошибка
        await message.answer(
            "Произошла ошибка при добавлении фильма. Пожалуйста, попробуйте снова.",
            reply_markup=get_admin_keyboard()
        )
    
    # Возвращаемся в админ-панель
    await state.set_state(AdminStates.in_admin_panel)

# Обработчик кнопки "Список фильмов"
@router.message(StateFilter(AdminStates.in_admin_panel), F.text == "Список фильмов")
async def list_movies(message: Message):
    # Получаем список всех фильмов
    movies = db.get_all_movies()
    
    if movies:
        # Если есть фильмы, формируем сообщение
        movies_text = "Список фильмов:\n\n"
        
        for i, movie in enumerate(movies, 1):
            movies_text += f"{i}. Код: {movie['code']} - {movie['title']} (Использований: {movie['usage_count']})\n"
        
        # Отправляем список фильмов
        await message.answer(movies_text)
    else:
        # Если фильмов нет
        await message.answer("В базе данных нет фильмов.")

# Обработчик кнопки "Удалить фильм"
@router.message(StateFilter(AdminStates.in_admin_panel), F.text == "Удалить фильм")
async def delete_movie_start(message: Message, state: FSMContext):
    # Получаем список всех фильмов
    movies = db.get_all_movies()
    
    if movies:
        # Если есть фильмы, формируем сообщение
        movies_text = "Выберите фильм для удаления. Введите код фильма:\n\n"
        
        for i, movie in enumerate(movies, 1):
            movies_text += f"{i}. Код: {movie['code']} - {movie['title']} (Использований: {movie['usage_count']})\n"
        
        # Отправляем список фильмов
        await message.answer(movies_text)
        
        # Устанавливаем состояние удаления фильма
        await state.set_state(AdminStates.deleting_movie)
    else:
        # Если фильмов нет
        await message.answer("В базе данных нет фильмов для удаления.")

# Обработчик ввода кода фильма для удаления
@router.message(StateFilter(AdminStates.deleting_movie))
async def delete_movie_code(message: Message, state: FSMContext):
    # Получаем код фильма
    code = message.text.strip()
    
    # Удаляем фильм из базы данных
    success = db.delete_movie(code)
    
    if success:
        # Если фильм успешно удален
        await message.answer(
            f"Фильм с кодом '{code}' успешно удален.",
            reply_markup=get_admin_keyboard()
        )
    else:
        # Если фильм не найден
        await message.answer(
            f"Фильм с кодом '{code}' не найден. Пожалуйста, проверьте код и попробуйте снова.",
            reply_markup=get_admin_keyboard()
        )
    
    # Возвращаемся в админ-панель
    await state.set_state(AdminStates.in_admin_panel)

# Обработчик кнопки "Рассылка"
@router.message(StateFilter(AdminStates.in_admin_panel), F.text == "Рассылка")
async def broadcast_start(message: Message, state: FSMContext):
    # Устанавливаем состояние рассылки
    await state.set_state(AdminStates.broadcasting)
    
    # Запрашиваем текст рассылки
    await message.answer("Введите текст для рассылки всем пользователям:")

# Обработчик ввода текста рассылки
@router.message(StateFilter(AdminStates.broadcasting))
async def broadcast_text(message: Message, state: FSMContext):
    # Получаем текст рассылки
    broadcast_text = message.text
    
    # Получаем список всех пользователей
    users = db.get_all_users()
    
    if users:
        # Счетчики для статистики
        total_users = len(users)
        successful_sends = 0
        
        # Отправляем сообщение о начале рассылки
        await message.answer(f"Начинаю рассылку {total_users} пользователям...")
        
        # Отправляем сообщение каждому пользователю
        for user in users:
            try:
                # Пытаемся отправить сообщение
                await message.bot.send_message(user['user_id'], broadcast_text)
                successful_sends += 1
            except Exception as e:
                # Если произошла ошибка, пропускаем пользователя
                print(f"Error sending message to user {user['user_id']}: {e}")
        
        # Отправляем статистику рассылки
        await message.answer(
            f"Рассылка завершена.\n"
            f"Успешно отправлено: {successful_sends} из {total_users}",
            reply_markup=get_admin_keyboard()
        )
    else:
        # Если пользователей нет
        await message.answer(
            "В базе данных нет пользователей для рассылки.",
            reply_markup=get_admin_keyboard()
        )
    
    # Возвращаемся в админ-панель
    await state.set_state(AdminStates.in_admin_panel)
