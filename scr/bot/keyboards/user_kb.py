from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

menu_student = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Новости", callback_data="news_user")],
    [InlineKeyboardButton(text="Контакты для связи", callback_data="contacts_for_communication_user")],
    [InlineKeyboardButton(text="Мой профиль", callback_data="my_profile")]
])

exit_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Выйти в меню", callback_data="menu")]])
