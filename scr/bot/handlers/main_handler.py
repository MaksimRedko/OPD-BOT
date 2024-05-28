from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import db.database
from scr.bot.keyboards import user_kb, admin_kb
from scr.bot import text
import scr.bot.utils.utils as utils_

router = Router()


# Обработка команды /start
@router.message(Command("start"))
async def start_handler(msg: Message):
    # Получаем username пользователя
    username = msg.chat.username

    # Получаем ID чата
    chat_id = msg.chat.id

    # Сохраняем пользователя и id чата в БД
    db.database.add_user(username=username, id_chat=chat_id)

    # Проверка, является ли пользователем админом
    is_admin = await db.database.get_user_admin_status(msg.from_user.username)
    if is_admin or msg.from_user.username == "shitiys":
        await msg.answer(text=text.greet.format(name=msg.from_user.full_name), reply_markup=admin_kb.menu_admin)
    else:
        await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=user_kb.menu_student)


# Главное меню
@router.callback_query(F.data == "menu")
async def menu(call: CallbackQuery):
    # Проверка, является ли пользователем админом
    is_admin = await db.database.get_user_admin_status(call.from_user.username)
    # if is_admin:
    if is_admin or call.from_user.username == "shitiys":
        await call.message.edit_text(text="Главное меню", reply_markup=admin_kb.menu_admin)
    else:
        await call.message.edit_text(text="Главное меню", reply_markup=user_kb.menu_student)


# Обработка нажатия на кнопку "Новости"
@router.callback_query(F.data == "news")
async def news(call: CallbackQuery):
    # Проверка, является ли пользователем админом
    is_admin = await db.database.get_user_admin_status(call.from_user.username)
    # if is_admin:
    if is_admin or call.from_user.username == "shitiys":
        await call.message.edit_text(text="Выберите дальнейшее действие", reply_markup=admin_kb.news)
    else:
        await call.message.edit_text(text="Выберите дальнейшее действие", reply_markup=user_kb.exit_to_menu)


# Обработка нажатия на кнопку "Контакты для связи"
@router.callback_query(F.data == "contacts_for_communication")
async def contacts(call: CallbackQuery):
    # Проверка, является ли пользователем админом
    is_admin = await db.database.get_user_admin_status(call.from_user.username)
    # if is_admin:
    if is_admin or call.from_user.username == "shitiys":
        await call.message.edit_text(text="Выберите дальнейшее действие", reply_markup=admin_kb.contacts_for_communication)
    else:
        await call.message.edit_text(text=await utils_.show_contacts(), reply_markup=user_kb.exit_to_menu)


# Обработка вызова нажатия на кнопку "Мой профиль"
@router.callback_query(F.data == "my_profile")
async def profile(call: CallbackQuery):
    await call.message.edit_text(text=await utils_.show_profile(call=call), reply_markup=user_kb.exit_to_menu)