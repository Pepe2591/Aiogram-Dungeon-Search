from typing import cast

from aiogram.types import (KeyboardButton, InlineKeyboardButton,
                           ReplyKeyboardMarkup, InlineKeyboardMarkup)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def inline_fabric(texts: dict[str, str], sizes = (2,), repeat = True) -> InlineKeyboardMarkup:
    """Создает инлайн разметку из полученного словаря и размеров."""

    kb = InlineKeyboardBuilder()

    for text, callback in texts.items():
        kb.add(InlineKeyboardButton(text=text, callback_data=callback))

    # Приводим sizes к кортежу, если передан один целой число
    if isinstance(sizes, int):
        sizes = (sizes,)

    return cast(InlineKeyboardMarkup, kb.adjust(*sizes, repeat=repeat).as_markup())


def keyboard_fabric(texts : tuple[str, ...], sizes : tuple[int, ...] | int, repeat = False) -> ReplyKeyboardMarkup:
    """Создает Реплай разметку, из полученных данных текста и размера"""
    kb = ReplyKeyboardBuilder()
    for text in texts:
        kb.add(KeyboardButton(text=text))

    sizes = (sizes,) if isinstance(sizes, int) else sizes
    return cast(ReplyKeyboardMarkup, kb.adjust(*sizes, repeat=repeat).as_markup(resize_keyboard=True))