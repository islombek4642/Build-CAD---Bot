
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from .strings import STRINGS

def get_main_keyboard(lang='uz'):
    keyboard = [
        [KeyboardButton(text=STRINGS[lang]['btn_create'])],
        [
            KeyboardButton(text=STRINGS[lang]['btn_help']),
            KeyboardButton(text=STRINGS[lang]['btn_settings'])
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_language_keyboard():
    keyboard = [
        [
            KeyboardButton(text="🇺🇿 O'zbekcha"),
            KeyboardButton(text="🇺🇸 English")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
