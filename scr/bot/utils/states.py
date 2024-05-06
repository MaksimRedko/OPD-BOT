from aiogram.fsm.state import StatesGroup, State


class NewsForm(StatesGroup):
    waiting_for_text = State()
    waiting_for_recipients = State()


class UserForm(StatesGroup):
    username = State()
    name = State()
    patronymic = State()
    surname = State()
    age = State()
    direction_of_study = State()
    phone = State()
    post = State()
    admin_status = State()


class ContactForm(StatesGroup):
    name = State()
    phone = State()
    post = State()


class Delete_user(StatesGroup):
    waiting_name_user_for_delete = State()


class UpdateUsersInfo(StatesGroup):
    get_username_for_updating = State()
    waiting_choices_for_update = State()
    got_choices_for_update = State()
    waiting_new_value = State()
    got_new_value = State()


class Delete_contact(StatesGroup):
    waiting_conatct_name_for_deliting = State()


class UpdateContactInfo(StatesGroup):
    get_contact_for_updating = State()
    waiting_param_for_update = State()
    waiting_new_value = State()
    updating = State()
