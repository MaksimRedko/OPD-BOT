from aiogram.types import CallbackQuery
import db.database as db


async def show_news():
    pass


async def show_contacts():
    contacts = [1, '2', [3]]
    result = '\n'.join(f'Контакт {index + 1}: {str(contact)}' for index, contact in enumerate(contacts))
    return result

def add_student(username, name, patronymic, surname, age, direction_of_study, phone, post, admin_status):
    db.add_user(username=username,
                name=name,
                patronymic=patronymic,
                surname=surname,
                age=age,
                direction_of_study=direction_of_study,
                phone=phone, post=post,
                admin_status=admin_status)

def delete_student(username=None, name=None, surname=None):
    pass

async def filter_aspirants():
    pass


async def show_profile(call: CallbackQuery):
    user_info = await db.get_users_info_(call.from_user.username)
    result = ""
    if user_info:

        for key, value in user_info.items():
            result += f"{key} : {value} \n"
        return result
    else:
        return "Пользователь не найден"
