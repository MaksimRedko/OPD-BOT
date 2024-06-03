import time

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import db.database
from db.database import add_user
from scr.bot.handlers.main_handler import menu
from scr.bot.keyboards import admin_kb
from scr.bot.utils.states import UserForm, ContactForm, NewsForm, Delete_user, UpdateUsersInfo, UpdateContactInfo
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

admin_router = Router()

# Минимальная страница и количество записей на странице во время пагинации данных
MIN_PAGE = 0
USERS_PER_PAGE = 5


# "След. страница" и "Пред. страница"
@admin_router.callback_query(lambda c: c.data.startswith(("prev_page_", "next_page_")))
async def prev_and_next_page_buttons(call: CallbackQuery, state: FSMContext, ):
    current_page = int(call.data.split("_page_")[1])  # Получаем текущий номер страницы
    action = call.data.split("_page_")[2]  # Получаем действие, которое выполняется на данный момент
    page_number = current_page

    # Изменяем номер страницы
    if call.data.startswith("prev_page_"):
        page_number = max(current_page - 1, MIN_PAGE)
    elif call.data.startswith("next_page_"):
        page_number = min(current_page + 1,
                          await db.database.calculate_max_page())

    # Продолжаем действие, с новой страницей
    if action == "delete_user":
        await show_users_for_delete(call=call, page_number=page_number)
    elif action == "update_user":
        await update_user_info(call=call, page_number=page_number, state=state)
    elif action == "delete_contact":
        await delete_contact_for_communication(call=call, page_number=page_number)
    elif action == "update_contact":
        await change__contact_for_communication()
    elif action == "view_user":
        await view_users(call=call, page_number=page_number)
    elif action == "view_contact":
        await view_contacts(call=call, page_number=page_number)


# region "Контакты для связи"
@admin_router.callback_query(F.data == "contacts_for_communication")
async def contacts_for_communication(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text="Выберите дальнейшее действие", reply_markup=admin_kb.contacts_for_communication)


# Функция для отображения списка контактов с пагинацией
async def show_contacts_with_pagination(call: CallbackQuery, page_number: int, action: str):
    # Получаем список контактов
    contacts = await db.database.get_contacts_with_pagination(page_number, USERS_PER_PAGE)

    if contacts:
        # Формируем список кнопок с пользователями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for contact in contacts:
            contact_name = contact[1]
            email = contact[2]
            phone = contact[3]
            button = InlineKeyboardButton(text=f"{contact_name}, {email} {phone}",
                                          callback_data=f"{action}_contact_{contact_name}")
            keyboard.inline_keyboard.append([button])

        # Добавляем кнопки переключения страниц
        prev_button = InlineKeyboardButton(text="<< Пред. стр.", callback_data=f"prev_page_{page_number}_page_{action}")
        next_button = InlineKeyboardButton(text="След. стр. >>", callback_data=f"next_page_{page_number}_page_{action}")

        keyboard.inline_keyboard.append([prev_button, next_button])
        text = "Выберите контакт:"
        return text, keyboard
    else:
        text = "Список контактов для связи пуст."
        return text, admin_kb.contacts_for_communication


# Функция для отображения информации о контакте в виде списка inline-кнопок
async def show_contacts_info(call: CallbackQuery, state: FSMContext, msg: Message = None):
    data = await state.get_data()
    contact_name = data['get_contact_for_updating']  # Получение contact_name

    contact_info = await db.database.get_contacts_info(contact_name=contact_name)

    await state.set_state(UpdateContactInfo.waiting_param_for_update)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for key, value in contact_info.items():
        button = InlineKeyboardButton(text=f"{key.capitalize()}: {value}",
                                      callback_data=f"contact_waiting_for_update_{key}")
        keyboard.inline_keyboard.append([button])
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="Вернуться назад", callback_data="change the contact for communication")])
    if call is None:
        await msg.answer(text="Информация успешно изменена,выберите, что хотите обновить", reply_markup=keyboard)
    else:
        await call.message.edit_text(text="Выберите, что хотите обновить", reply_markup=keyboard)


# region "Добавить новый"
@admin_router.callback_query(F.data == "add new contact for communication")
async def add_new_contact_for_communication(call: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние в "name", ждем название контакта
    await state.set_state(ContactForm.name)
    await call.message.edit_text(text="Введите наименование контакта для связи",
                                 reply_markup=InlineKeyboardMarkup(
                                     inline_keyboard=[admin_kb.cancel_contacts_for_communication]))


# Введено наименование контакта для связи
@admin_router.message(StateFilter(ContactForm.name))
async def get_contacts_name_and_wait_phone(msg: Message, state: FSMContext):
    # Введенное текстовое сообщение от пользователя сохраняем как имя контакта для связи
    await state.update_data(name=msg.text)

    # Устанавливаем состояние в "phone", ждем телефон контакта
    await state.set_state(ContactForm.phone)
    await msg.answer(text="Введите телефон для связи",
                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_contacts_for_communication]))


# Введен телефон контакта для связи
@admin_router.message(StateFilter(ContactForm.phone))
async def get_contacts_phone_and_wait_email(msg: Message, state: FSMContext):
    # Введенное текстовое сообщение от пользователя сохраняем как телефон контакта для связи
    await state.update_data(phone=msg.text)

    # Устанавливаем состояние в "email", ждем почту контакта
    await state.set_state(ContactForm.post)
    await msg.answer(text="Введите почту для связи",
                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_contacts_for_communication]))


# Введена почта контакта для связи
@admin_router.message(StateFilter(ContactForm.post))
async def get_contacts_email_and_save_to_db(msg: Message, state: FSMContext):
    # Введенное текстовое сообщение от пользователя сохраняем как почту контакта для связи
    await state.update_data(post=msg.text)

    # Получаем сохраненные данные
    data = await state.get_data()

    # Загружаем контакт в базу данных
    db.database.add_contact(contact_name=data["name"], phone=data["phone"], email=data["post"])

    # Очищаем состояние и возвращаемся в "Контакты для связи"
    await state.clear()
    await msg.answer(text="Контакт для связи добавлен", reply_markup=admin_kb.contacts_for_communication)


# endregion


# region "Изменить существующий"
@admin_router.callback_query(F.data == "change the contact for communication")
async def change__contact_for_communication(call: CallbackQuery, state: FSMContext, page_number=0):
    await state.set_state(UpdateContactInfo.get_contact_for_updating)
    text, keyboard = await show_contacts_with_pagination(call=call, page_number=page_number, action="update_contact")
    if text == "Список пользователей пуст.":
        await call.message.edit_text(text=text, reply_markup=admin_kb.contacts_for_communication)
    else:
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Выбран контакт из списка inline-кнопок, выводим информацию о нем, тоже в виде inline-кнопок
@admin_router.callback_query(lambda c: c.data.startswith("update_contact_"))
async def get_contact_for_updating(call: CallbackQuery, state: FSMContext):
    contact_name = call.data.replace("update_contact_contact_", "")
    await state.update_data(get_contact_for_updating=contact_name)
    await state.set_state(UpdateContactInfo.waiting_param_for_update)
    await show_contacts_info(call=call, state=state)


# Выбран параметр из inline-кнопок(show_contacts_info), ждем новую информацию для обновления
@admin_router.callback_query(StateFilter(UpdateContactInfo.waiting_param_for_update))
async def get_param_for_update(call: CallbackQuery, state: FSMContext):
    key = call.data.replace("contact_waiting_for_update_", "")
    await state.update_data(waiting_param_for_update=key)

    await state.set_state(UpdateContactInfo.waiting_new_value)
    await call.message.edit_text(text="Введите новую информацию", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="change the contact for communication")]]))


# Введена новая информация для обновления, обновляем и возвращаемся к списку параметров контакта
@admin_router.message(StateFilter(UpdateContactInfo.waiting_new_value))
async def get_new_value_for_updating_contacts_param(msg: Message, state: FSMContext):
    data = await state.get_data()
    contact_name = data["get_contact_for_updating"]
    key = data["waiting_param_for_update"]
    value = msg.text

    if key == "contact_name":
        await state.update_data(get_contact_for_updating=value)

    await db.database.update_contacts_info(contact_name=contact_name, key=key, new_value=value)
    await show_contacts_info(call=None, msg=msg, state=state)


# endregion

# region "Удалить контакт"
@admin_router.callback_query(F.data == "delete contact for communication")
async def delete_contact_for_communication(call: CallbackQuery, page_number=0):
    # Получаем список контактов в виде списка из inline-кнопок
    text, keyboard = await show_contacts_with_pagination(call=call, page_number=page_number, action="delete_contact")

    if text == "Список контактов пуст.":
        await call.message.edit_text(text=text, reply_markup=admin_kb.contacts_for_communication)
    else:
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Если произошло нажатие на inline-кнопку из списка контактов
@admin_router.callback_query(lambda c: c.data.startswith("delete_contact_"))
async def get_contact_for_delete(call: CallbackQuery):
    # Получаем наименование контакта для связи
    contact_name = call.data.replace("delete_contact_contact_", "")

    # Удаляем контакт из базы данных и возвращаемся в "Контакты для связи"
    db.database.delete_contact(contact_name=contact_name)
    await call.message.edit_text(text="Контакт удален", reply_markup=admin_kb.contacts_for_communication)


# endregion


# region "Просмотреть существующие"
@admin_router.callback_query(F.data == "view contacts for communication")
async def view_contacts(call: CallbackQuery, page_number=0):
    # Вывод всех контактов в виде inline-кнопок
    text, keyboard = await show_contacts_with_pagination(call=call, page_number=page_number, action="view_contact")

    if text == "Список контактов пуст.":
        await call.message.edit_text(text=text, reply_markup=admin_kb.contacts_for_communication)
    else:
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Была нажата соответсвующая кнопка, выводим информацию о контакте в виде сообщения
@admin_router.callback_query(lambda c: c.data.startswith("view_contact_"))
async def got_contact_for_view(call: CallbackQuery):
    contact_name = call.data.replace("view_contact_contact_", "")
    contact_info = await db.database.get_contacts_info(contact_name=contact_name)
    result = ""
    if contact_info:
        for key, value in contact_info.items():
            result += f"{key} : {value} \n"
    back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться назад", callback_data="view contacts for communication")]])
    await call.message.edit_text(text=result, reply_markup=back_button)


# endregion
# endregion


# region "Пользователи"

@admin_router.callback_query(F.data == "users")
async def update_profiles(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text="Выберите дальнейшее действие", reply_markup=admin_kb.users)


# Функция для показа списка пользователей с пагинацией
async def show_users_with_pagination(call: CallbackQuery, page_number: int, action):
    # Получаем список пользователей с пагинацией
    users = await db.database.get_users_with_pagination(page_number, USERS_PER_PAGE)

    if users:
        # Формируем список кнопок с пользователями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for user in users:
            username = user[1]
            name = user[2]
            surname = user[4]
            button = InlineKeyboardButton(text=f"{username}, {name} {surname}",
                                          callback_data=f"{action}_user_{username}")
            keyboard.inline_keyboard.append([button])

        # Добавляем кнопки пагинации
        prev_button = InlineKeyboardButton(text="<< Пред.", callback_data=f"prev_page_{page_number}_page_{action}")
        next_button = InlineKeyboardButton(text="След. >>", callback_data=f"next_page_{page_number}_page_{action}")
        keyboard.inline_keyboard.append([prev_button, next_button])


        text = "Выберите пользователя:"
        return text, keyboard
    else:
        text = "Список пользователей пуст."
        return text, admin_kb.users


# region "Добавить новый"

@admin_router.callback_query(F.data == "add new users")
async def add_user_start(call: CallbackQuery, state: FSMContext):
    # await call.answer()

    # Устанавливаем состояние в "username", ждем ввод username
    await state.set_state(UserForm.username)
    await call.message.edit_text("Введите Telegram username пользователя (без @):",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено username
@admin_router.message(StateFilter(UserForm.username))
async def got_username_wait_name(message: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как username пользователя
    await state.update_data(username=message.text)

    # Устанавливаем состояние в "name", ждем ввод имени
    await state.set_state(UserForm.name)
    await message.answer("Введите имя пользователя:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено name
@admin_router.message(StateFilter(UserForm.name))
async def got_name_wait_patronymic(message: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как имя пользователя
    await state.update_data(name=message.text)

    # Устанавливаем состояние в "patronymic", ждем ввод отчества
    await state.set_state(UserForm.patronymic)
    await message.answer("Введите отчество пользователя:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено patronymic
@admin_router.message(StateFilter(UserForm.patronymic))
async def got_patronymic_wait_surname(message: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как отчество пользователя
    await state.update_data(patronymic=message.text)

    # Устанавливаем состояние в "surname", ждем ввод фамилии
    await state.set_state(UserForm.surname)
    await message.answer("Введите фамилию пользователя:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено surname
@admin_router.message(StateFilter(UserForm.surname))
async def got_surname_wait_age(message: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как фамилию пользователя
    await state.update_data(surname=message.text)

    # Устанавливаем состояние в "age", ждем ввод возраста
    await state.set_state(UserForm.age)
    await message.answer("Введите возраст пользователя:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено age
@admin_router.message(StateFilter(UserForm.age))
async def got_age_wait_direction_of_study(message: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как возраст пользователя
    await state.update_data(age=message.text)

    # Устанавливаем состояние в "direction_of_study", ждем направление обучения
    await state.set_state(UserForm.direction_of_study)
    await message.answer("Введите направление обучения пользователя:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено direction_of_study
@admin_router.message(StateFilter(UserForm.direction_of_study))
async def got_direction_of_study_wait_phone(msg: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как направление обучения пользователя
    await state.update_data(direction_of_study=msg.text)

    # Устанавливаем состояние в "phone", ждем телефон
    await state.set_state(UserForm.phone)
    await msg.answer("Введите телефон пользователя:",
                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено phone
@admin_router.message(StateFilter(UserForm.phone))
async def got_phone_wait_post(message: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как телефон пользователя
    await state.update_data(phone=message.text)

    # Устанавливаем состояние в "post", ждем почту
    await state.set_state(UserForm.post)
    await message.answer("Введите почту пользователя:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Введено post
@admin_router.message(StateFilter(UserForm.post))
async def got_post_wait_admin_satus(message: Message, state: FSMContext):
    # Сохраняем полученное текстовое сообщение как почту пользователя
    await state.update_data(post=message.text)

    # Создаем клавиатуру для назначения админ-статуса пользователя
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сделать администратором", callback_data="Да")],
        [InlineKeyboardButton(text="Сделать обычным пользователем", callback_data="Нет")],
        [InlineKeyboardButton(text='Отменить добавление пользователя', callback_data="users")]
    ])

    # Устанавливаем состояние в "admin_status", ждем нажатие кнопки
    await state.set_state(UserForm.admin_status)
    await message.answer(text="Сделать данного пользователя администратором?", reply_markup=buttons)


# Введено admin_status
@admin_router.callback_query(StateFilter(UserForm.admin_status))
async def got_admin_status_add_to_db(call: CallbackQuery, state: FSMContext):
    # Сохраняем нажатую кнопку как админ-статус пользователя
    await state.update_data(admin_status=call.data)

    # Получаем сохраненные данные о пользователе и добавляем пользователя в БД
    user_data = await state.get_data()
    add_user(
        username=user_data['username'],
        name=user_data['name'],
        patronymic=user_data['patronymic'],
        surname=user_data['surname'],
        age=user_data['age'],
        direction_of_study=user_data['direction_of_study'],
        phone=user_data['phone'],
        post=user_data['post'],
        admin_status=user_data['admin_status'])

    # Очищаем состояние и переходим в "Пользователи"
    await state.clear()
    await call.message.edit_text("Пользователь добавлен", reply_markup=admin_kb.users)


# endregion


# region "Удалить пользователя"
@admin_router.callback_query(F.data == "delete user")
async def delete_user(call: CallbackQuery):
    await call.message.edit_text("Выберите способ удаления пользователя:", reply_markup=admin_kb.delete_user)


# Выбран способ удаления через написание юзернейма, ждем ввод от пользователя
@admin_router.callback_query(F.data == "delete_user_by_username")
async def delete_user_by_username_or_name(call: CallbackQuery, state: FSMContext):
    # Ждем ввода username которого надо удалить
    await state.set_state(state=Delete_user.waiting_name_user_for_delete)
    await call.message.edit_text(text="Напишите username пользователя, которого хотите удалить:",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_users]))


# Выбран способ выбора из списка inline-кнопок, выводим список пользователей
@admin_router.callback_query(F.data == "show_users_for_delete")
async def show_users_for_delete(call: CallbackQuery, page_number=0):
    # Выводим список пользователей для удаления
    text, keyboard = await show_users_with_pagination(call, page_number, action="delete_user")

    if text == "Список пользователей пуст.":
        await call.message.edit_text(text=text, reply_markup=admin_kb.users)
    else:
        keyboard.inline_keyboard.append(admin_kb.cancel_users)
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Обработчик нажатия на пользователя из списка inline-кнопок
@admin_router.callback_query(lambda c: c.data.startswith("delete_user_"))
async def got_user_from_inline_button(call: CallbackQuery, state: FSMContext):
    username = call.data.replace("delete_user_user_", "")  # Получаем username пользователя

    # Удаляем пользователя из базы данных
    await db.database.delete_user(username)
    await state.clear()  # Очищаем состояние
    await call.message.edit_text(text="Пользователь удален", reply_markup=admin_kb.users)


# Обработчик ввода username пользователя путем ввода в чат
@admin_router.message(StateFilter(Delete_user.waiting_name_user_for_delete))
async def deleting_user_from_message(msg: Message, state: FSMContext):
    # Удаляем пользователя
    await db.database.delete_user(msg.text)

    await state.clear()  # Очищаем состояние
    await msg.answer(text="Пользователь удален", reply_markup=admin_kb.users)


# endregion


# region Изменение данных пользователя
@admin_router.callback_query(F.data == "change user's info")
async def update_user_info(call: CallbackQuery, state: FSMContext, page_number=0):
    await state.set_state(UpdateUsersInfo.get_username_for_updating)
    text, keyboard = await show_users_with_pagination(call=call, page_number=page_number, action="update_user")

    if text == "Список пользователей пуст.":
        await call.message.edit_text(text=text, reply_markup=admin_kb.users)
    else:
        keyboard.inline_keyboard.append(admin_kb.cancel_users)
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Выбран пользователь из списка inline-кнопок, выводим список параметров пользователя, в виде списка inline-кнопок
@admin_router.callback_query(lambda c: c.data.startswith("update_user_"))
async def update_user_handler(call: CallbackQuery, state: FSMContext):
    if call.data == "update_user_info":
        await update_user_info(call=call, state=state)
    username = call.data.replace("update_user_user_", "")  # Получаем username пользователя
    await state.update_data(get_username_for_updating=username)
    await state.set_state(UpdateUsersInfo.waiting_choices_for_update)  # Ждем, что будем обновлять
    await show_users_info(call=call, state=state)


# Функция вывода информации о пользователе, в виде inline-кнопок
@admin_router.callback_query(StateFilter(UpdateUsersInfo.waiting_choices_for_update))
async def show_users_info(call: CallbackQuery, state: FSMContext, msg: Message = None):
    data = await state.get_data()
    username = data['get_username_for_updating']  # Получение username из сохранённых данных
    user_info = await db.database.get_users_info_(username=username)
    await state.set_state(UpdateUsersInfo.got_choices_for_update)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for key, value in user_info.items():
        button = InlineKeyboardButton(text=f"{key.capitalize()}: {value}",
                                      callback_data=f"waiting_for_update_{key}")
        keyboard.inline_keyboard.append([button])
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="Вернуться назад", callback_data="update_user_info")])
    if call is None:
        await msg.answer(text="Информация успешно изменено,выберите, что хотите обновить", reply_markup=keyboard)
    else:
        await call.message.edit_text(text="Выберите, что хотите обновить", reply_markup=keyboard)


# Выбран параметр, ждем ввода новой информации
@admin_router.callback_query(lambda c: c.data.startswith("waiting_for_update_"))
async def waiting_new_user_info(call: CallbackQuery, state: FSMContext):
    value = call.data.replace("waiting_for_update_", "")  # Получаем названия пункта, которsq хотим обновить
    await state.update_data(waiting_choices_for_update=value)
    await state.set_state(UpdateUsersInfo.got_new_value)
    data = await state.get_data()  # Использование await для получения данных
    username = data['get_username_for_updating']  # Получение username из сохранённых данных
    cancel_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Отменить изменение", callback_data=f"update_user_{username}")]])
    await call.message.edit_text(text="Введите новую информацию", reply_markup=cancel_button)

# Информация получена, обновляем соответсвующий параметр и выводим список параметров пользователя
@admin_router.message(StateFilter(UpdateUsersInfo.got_new_value))
async def got_new_user_info_and_update(msg: Message, state: FSMContext):
    data = await state.get_data()
    username = data["get_username_for_updating"]
    key = data["waiting_choices_for_update"]
    value = msg.text
    if key == "username":
        await state.update_data(get_username_for_updating=value)
    await db.database.update_user_info(username=username, key=key, new_value=value)
    await show_users_info(call=None, state=state, msg=msg)


# endregion

# region "Просмотреть существующие"
@admin_router.callback_query(F.data == "view users")
async def view_users(call: CallbackQuery, page_number=0):
    text, keyboard = await show_users_with_pagination(call=call, page_number=page_number, action="view_user")

    if text == "Список пользователей пуст.":
        await call.message.edit_text(text=text, reply_markup=admin_kb.users)
    else:
        keyboard.inline_keyboard.append(admin_kb.cancel_users)
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Выбран пользователь из списка inline-кнопок, выводим информацию о нем, в виде сообщения
@admin_router.callback_query(lambda c: c.data.startswith("view_user_"))
async def got_users_for_view(call: CallbackQuery):
    username = call.data.replace("view_user_user_", "")
    user_info = await db.database.get_users_info_(username)
    result = ""
    if user_info:
        for key, value in user_info.items():
            result += f"{key} : {value} \n"
    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Вернуться назад", callback_data="view users")]])
    await call.message.edit_text(text=result, reply_markup=back_button)


# endregoin
# endregion

# endregion

# region "Новости"

@admin_router.callback_query(F.data == "news")
async def write_news(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text="Выберите дальнейшее действие", reply_markup=admin_kb.news)


# Выбор получателя для новости
@admin_router.callback_query(F.data == "select_recipient")
async def select_recipient(call: CallbackQuery, state: FSMContext):
    await state.set_state(NewsForm.waiting_for_recipients)
    await call.message.edit_text(text="Введите username пользователей(через запятую), которым хотите отправить новость",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_news]))


# Получили пользователей, выводим меню новостей
@admin_router.message(StateFilter(NewsForm.waiting_for_recipients))
async def got_recipients(msg: Message, state: FSMContext):
    await state.update_data(waiting_for_recipients=msg.text.replace(" ", "").split(","))
    await msg.answer(text="Пользователи получены", reply_markup=admin_kb.news)


# Ждем ввод новости/сообщения от пользователя
@admin_router.callback_query(F.data == "write_text_news")
async def write_text_news(call: CallbackQuery, state: FSMContext):
    await state.set_state(NewsForm.waiting_for_text)
    await call.message.edit_text(text="Напишите текст новости",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_news]))


# Получен текст сообщения от пользователя, возвращаем его обратно в меню новостей
@admin_router.message(StateFilter(NewsForm.waiting_for_text))
async def got_text_of_news(msg: Message, state: FSMContext):
    await state.update_data(waiting_for_text=msg.text)
    await msg.answer(text="Текст новости сохранен", reply_markup=admin_kb.news)


# Вывод информации о новости, перед отправкой
@admin_router.callback_query(F.data == "send_news")
async def send_news(call: CallbackQuery, state: FSMContext):
    news_data = await state.get_data()
    text_news = "Текст новости:\n" + news_data["waiting_for_text"] + "\n"
    user_data_list = []
    for username in news_data["waiting_for_recipients"]:
        user_data = await db.database.get_users_info_(username)
        if user_data:
            user_data_list.append(user_data)
    recipients_list = "Пользователи:\n"
    for user_data in user_data_list:
        for key, value in user_data.items():
            recipients_list += f"{key} : {value} \n"
        recipients_list += "\n"
    await call.message.edit_text(text=(text_news + recipients_list), reply_markup=admin_kb.send_news)


# Отправка сообщения всем указанным пользователям(всем, кто начал чат с ботом)
@admin_router.callback_query(F.data == "sending_news")
async def sending_news(call: CallbackQuery, state: FSMContext):
    news_data = await state.get_data()
    text_news = news_data["waiting_for_text"]
    date = time.strftime("%M:%H|%d.%m.%Y", time.localtime())
    is_read_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Я прочитал/прочитала", callback_data=f"i_read_{date}")]])
    usernames = []
    for username in news_data["waiting_for_recipients"]:
        user_data = await db.database.get_users_info_(username)
        if user_data:
            usernames.append([user_data["username"], user_data["id_chat"]])

    await db.database.add_news(text=text_news, recipients=str(usernames), date=date)
    for username in usernames:
        try:
            print(username[1])
            await call.bot.send_message(chat_id=username[1],
                                        text=text_news + "\n\nЕсли прочитали, нажмите на кнопку ниже.",
                                        reply_markup=is_read_button)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {username}: {e}")
    await call.message.edit_text(text="Новость доставлена", reply_markup=admin_kb.news)


# Пользователь нажал на "я прочитал"
@admin_router.callback_query(lambda c: c.data.startswith("i_read_"))
async def get_who_read(call: CallbackQuery):
    # Получаем дату отправки сообщения, которую прочитал пользователь
    when_read = call.data.replace("i_read_", "")

    # Обновляем запись в базе данных, отмечая пользователя, который прочитал новость
    await db.database.read_news(date=when_read, chat_id=call.message.chat.id)

    # Переход на главное меню
    await menu(call=call)


# Функция вывода новостей с пагинацией
async def show_news_with_pagination(call: CallbackQuery, page_number: int, action: str):
    # Получаем список новостей
    news_list = await db.database.get_news_with_pagination(page_number, USERS_PER_PAGE)

    if news_list:
        # Формируем список кнопок с новостями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for news in news_list:
            text = news[1]
            date = news[2]
            recipients = news[3]
            read_recipients = news[4]
            button = InlineKeyboardButton(text=f"Новость от {date}",
                                          callback_data=f"{action}_of_{date}")
            keyboard.inline_keyboard.append([button])
        # Добавляем кнопки переключения страниц
        prev_button = InlineKeyboardButton(text="<< Пред. стр.", callback_data=f"prev_page_{page_number}_page_{action}")
        next_button = InlineKeyboardButton(text="След. стр. >>", callback_data=f"next_page_{page_number}_page_{action}")

        keyboard.inline_keyboard.append([prev_button, next_button])
        text = "Выберите новость для просмотра:"
        return text, keyboard
    else:
        text = "Список новостей пуст."
        return text, admin_kb.news


# Вывод списка новостей в виде inline-кнопок
@admin_router.callback_query(F.data == "view news")
async def view_news(call: CallbackQuery, page_number=0):
    text, keyboard = await show_news_with_pagination(call=call, page_number=page_number, action="view_news")

    if text == "Список новостей пуст.":
        await call.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[admin_kb.cancel_news]))
    else:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text='Назад', callback_data="news")])
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Вывод информации о новости, выбранной из списка
@admin_router.callback_query(lambda c: c.data.startswith("view_news_"))
async def got_news_for_view(call: CallbackQuery):
    date = call.data.replace("view_news_of_", "")
    news_info = await db.database.get_news_info(date=date)
    result = ""
    if news_info:
        for key, value in news_info.items():
            result += f"{key} : {value} \n"
    back_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Вернуться назад", callback_data="view news")]])
    await call.message.edit_text(text=result, reply_markup=back_button)
