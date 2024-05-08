from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

# Клавиатура "Главное меню"
menu_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Новости", callback_data="news"),
     InlineKeyboardButton(text="Контакты для связи", callback_data="contacts_for_communication")],
    [InlineKeyboardButton(text="Пользователи", callback_data="users"),
     InlineKeyboardButton(text="Мой профиль", callback_data="my_profile")]
])

# Клавиатура "Новости"
news = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выбрать получателя", callback_data="select_recipient"),
     InlineKeyboardButton(text="Написать сообщение/новость", callback_data="write_text_news")],
    [InlineKeyboardButton(text="Проверить и отослать новость", callback_data="send_news"),
     InlineKeyboardButton(text="Просмотреть новости", callback_data="view news")],
     [InlineKeyboardButton(text="Выйти в меню", callback_data="menu")]
])

# Кнопка отмены для Новостей
cancel_news = [InlineKeyboardButton(text='Отменить', callback_data="news")]

# Клавиатура "Контакты для связи"
contacts_for_communication = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить новый", callback_data="add new contact for communication"),
     InlineKeyboardButton(text="Изменить существующий", callback_data="change the contact for communication")],
    [InlineKeyboardButton(text="Просмотреть существующие", callback_data="view contacts for communication"),
     InlineKeyboardButton(text="Удалить контакт", callback_data="delete contact for communication")],
    [InlineKeyboardButton(text="Выйти в меню", callback_data="menu")]
])

# Кнопка отмены для контактов
cancel_contacts_for_communication = [InlineKeyboardButton(text='Отменить', callback_data="contacts_for_communication")]

# Клавиатура "Пользователи"
users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить новый", callback_data="add new users"),
     InlineKeyboardButton(text="Изменить существующий", callback_data="change user's info")],
    [InlineKeyboardButton(text="Просмотреть существующие", callback_data="view users"),
     InlineKeyboardButton(text="Удалить пользователя", callback_data="delete user")],
     [InlineKeyboardButton(text="Выйти в меню", callback_data="menu")]
])

# Кнопка отмены для действий с пользователями
cancel_users = [InlineKeyboardButton(text='Отменить', callback_data="users")]

# Клавиатура "Удалить пользователя"
delete_user = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Удалить по username", callback_data="delete_user_by_username"),
     InlineKeyboardButton(text="Выбрать из списка пользователей", callback_data="show_users_for_delete")],
    [InlineKeyboardButton(text='Отменить', callback_data="delete user")]
])

# Клавиатура "Мой профиль"
my_profile = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Выйти в меню", callback_data="menu")]])

send_news = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отправить новость", callback_data="sending_news")],
    cancel_news
])








