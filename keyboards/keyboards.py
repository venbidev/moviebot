from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для команды /start"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Ввести код")]],
        resize_keyboard=True
    )

def get_check_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для проверки подписки на каналы"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Проверить заявки", callback_data="check_requests")]
        ]
    )

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для админ-панели"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить фильм")],
            [KeyboardButton(text="Список фильмов")],
            [KeyboardButton(text="Удалить фильм")],
            [KeyboardButton(text="Рассылка")],
            [KeyboardButton(text="Выйти из админ-панели")]
        ],
        resize_keyboard=True
    )
