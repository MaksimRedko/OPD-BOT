from aiogram import F, Router
from aiogram.types import CallbackQuery
import db.database as db
from scr.bot.handlers.admin_handler import show_news_with_pagination, show_contacts_with_pagination
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

user_router = Router()


@user_router.callback_query(F.data == "news_user")
async def news_user(call: CallbackQuery, page_number=0):
    text, keyboard = await show_news_with_pagination(call=call, page_number=page_number, action="view_newsuser")

    for row in keyboard.inline_keyboard:
        for button in row:
            if button.text in ['<< Пред. стр.', 'След. стр. >>']:
                button.callback_data = 'user_' + button.callback_data

    if not text == "Список новостей пуст.":
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text='Вернуться назад', callback_data="menu")])
    await call.message.edit_text(text=text, reply_markup=keyboard)


@user_router.callback_query(lambda c: c.data.startswith("view_newsuser"))
async def got_news_for_view(call: CallbackQuery):
    print(call.data)
    date = call.data.replace("view_newsuser_of_", "")
    news_info = await db.get_news_info(date=date)
    result = ""
    if news_info:
        for key, value in news_info.items():
            result += f"{key} : {value} \n"
    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Вернуться назад", callback_data="news_user")]])
    await call.message.edit_text(text=result, reply_markup=back_button)


@user_router.callback_query(F.data == "contacts_for_communication_user")
async def contacts_for_communication_user(call: CallbackQuery, page_number=0):
    text, keyboard = await show_contacts_with_pagination(call=call, page_number=page_number, action="view_contactuser")
    print(keyboard.inline_keyboard)

    if not text == "Список контактов пуст.":
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text='Вернуться назад', callback_data="menu")])
    print("НОрм НОРм выводим список контактов")
    await call.message.edit_text(text=text, reply_markup=keyboard)


@user_router.callback_query(lambda c: c.data.startswith("view_contactuser"))
async def got_contact_for_view(call: CallbackQuery):
    print("НОрм НОРм список контактов вывелся, щас выводим инфу про контакт")
    contact_name = call.data.replace("view_contactuser_contact_", "")
    contact_info = await db.get_contacts_info(contact_name=contact_name)
    back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться назад", callback_data="contacts_for_communication_user")]])
    if contact_info:
        result = ""
        for key, value in contact_info.items():
            result += f"{key} : {value} \n"

        await call.message.edit_text(text=result, reply_markup=back_button)
    else:
        await call.message.edit_text(text="Информация о контакте не найдена.", reply_markup=back_button)


@user_router.callback_query(lambda c: c.data.startswith(("user_prev_page_", "user_next_page_")))
async def prev_and_next_page_buttons(call: CallbackQuery):
    current_page = int(call.data.split("_page_")[1])  # Получаем текущий номер страницы
    action = call.data.split("_page_")[2]  # Получаем действие, которое выполняется на данный момент
    page_number = current_page

    # Изменяем номер страницы
    if call.data.startswith("prev_page_"):
        page_number = max(current_page - 1, 0)
    elif call.data.startswith("next_page_"):
        page_number = min(current_page + 1,
                          await db.calculate_max_page())

    # Продолжаем действие, с новой страницей
    if action == "view_newsuser":
        await news_user(call=call, page_number=page_number)
    elif action == "view_contactuser":
        await contacts_for_communication_user(call=call, page_number=page_number)
