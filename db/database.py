import math
import sqlite3
import time


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Создаем таблицы
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT,
                 name TEXT,
                 patronymic TEXT,
                 surname TEXT,
                 age TEXT,
                 direction_of_study TEXT,
                 phone TEXT,
                 post TEXT,
                 admin_status TEXT,
                 id_chat TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 contact_name TEXT,
                 email TEXT,
                 phone TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS news
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     news_text TEXT,
                     publish_date TEXT,
                     recipients TEXT,
                     who_read TEXT)''')

    conn.commit()
    conn.close()


# Добавление пользователя
def add_user(username=None, name=None, patronymic=None, surname=None, age=None, direction_of_study=None, phone=None,
             post=None, admin_status=None, id_chat=None):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM users WHERE username = ? OR id_chat = ?''', (username, id_chat))
    existing_contact = c.fetchone()

    if not existing_contact:
        # Добавляем пользователя
        c.execute('''INSERT INTO users (username, name, patronymic, surname, age, direction_of_study, phone, post, admin_status, id_chat)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (username, name, patronymic, surname, age, direction_of_study, phone, post, admin_status, id_chat))

    conn.commit()
    conn.close()


def add_contact(contact_name, phone, email):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM contacts WHERE contact_name = ?''', (contact_name,))
    existing_contact = c.fetchone()

    if not existing_contact:
        c.execute('''INSERT INTO contacts (contact_name, phone, email) VALUES (?, ?, ?)''',
                  (contact_name, phone, email))

    conn.commit()
    conn.close()


def delete_contact(contact_name):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''DELETE FROM contacts WHERE contact_name = ?''', (contact_name,))

    conn.commit()
    conn.close()


async def get_user_admin_status(username=None, id=None):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''SELECT admin_status FROM users WHERE username = ?''', (username,))
    result = c.fetchall()
    is_admin = False
    if result:
        is_admin = result[0][0] == 'Да'

    conn.close()
    return is_admin


# Функция удаления пользователя по username
async def delete_user(name_string):
    split_name_string = str.split(name_string.lower(), ',')
    username = None
    name = None
    surname = None

    if len(split_name_string) == 1:
        username = str.split(name_string, ',')[0]

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    # Проверка наличия данных перед выполнением запроса
    if username:
        c.execute("DELETE FROM users WHERE username = ?", (username,))
    elif name and surname:
        c.execute("DELETE FROM users WHERE name = ? AND surname = ?", (name, surname))
    conn.commit()
    conn.close()


async def get_users_with_pagination(page_number, page_size):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Вычисляем смещение для текущей страницы
    offset = (page_number - 1) * page_size

    # Выполняем запрос на извлечение пользователей с учетом пагинации
    c.execute('''SELECT * FROM users LIMIT ? OFFSET ?''', (page_size, offset))
    users = c.fetchall()

    conn.close()

    return users


async def get_contacts_with_pagination(page_number, page_size):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    page_number = 0 if page_number == 0 else page_number
    # Вычисляем смещение для текущей страницы
    offset = (page_number - 1) * page_size

    c.execute('''SELECT * FROM contacts LIMIT ? OFFSET ?''', (page_size, offset))
    contacts = c.fetchall()

    conn.close()

    return contacts


async def get_news_with_pagination(page_number, page_size):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    page_number = 0 if page_number == 0 else page_number
    # Вычисляем смещение для текущей страницы
    offset = (page_number - 1) * page_size

    c.execute('''SELECT * FROM news LIMIT ? OFFSET ?''', (page_size, offset))
    news = c.fetchall()

    conn.close()

    return news


async def get_contacts_info(contact_name):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM contacts WHERE contact_name = ?''', (contact_name,))
    contact_info = c.fetchone()
    conn.close()

    if contact_info:
        # Формируем словарь, где названия столбцов будут ключами
        columns = [col[0] for col in c.description]
        print(columns)
        print(contact_info)
        contact_dict = dict(zip(columns, contact_info))
        print(contact_dict)
        print()
        return contact_dict
    else:
        return None  # Возвращаем None, если пользователь с таким username не найден


async def update_contacts_info(contact_name, key, new_value):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Формирование SQL запроса с использованием безопасного параметра
    # Нельзя использовать параметризацию для имени столбца, поэтому используем f-string.
    # Однако нужно быть очень осторожным, чтобы избежать SQL-инъекций, проверяя имя столбца.
    allowed_keys = ["contact_name", "email", "phone"]
    if key in allowed_keys:
        query = f"UPDATE contacts SET {key} = ? WHERE contact_name = ?"
        c.execute(query, (new_value, contact_name))
        conn.commit()
    else:
        raise ValueError(f"Некорректное имя поля: {key}")

    conn.close()


async def get_users_info_(username):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM users WHERE username = ?''', (username,))
    user_info = c.fetchone()  # Получаем только одну строку, так как ожидаем, что username уникален

    conn.close()

    if user_info:
        # Формируем словарь, где названия столбцов будут ключами
        columns = [col[0] for col in c.description]
        print(columns)
        print(user_info)
        user_dict = dict(zip(columns, user_info))
        return user_dict
    else:
        return None  # Возвращаем None, если пользователь с таким username не найден


async def get_news_info(date):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM news WHERE publish_date = ?''', (date,))
    news_info = c.fetchone()  # Получаем только одну строку, так как ожидаем, что username уникален

    conn.close()

    if news_info:
        # Формируем словарь, где названия столбцов будут ключами
        columns = [col[0] for col in c.description]
        print(columns)
        print(news_info)
        news_dict = dict(zip(columns, news_info))
        return news_dict
    else:
        return None  # Возвращаем None, если пользователь с таким username не найден


async def update_user_info(username, key, new_value):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Формирование SQL запроса с использованием безопасного параметра
    # Нельзя использовать параметризацию для имени столбца, поэтому используем f-string.
    # Однако нужно быть очень осторожным, чтобы избежать SQL-инъекций, проверяя имя столбца.
    allowed_keys = ["username", "name", "patronymic", "surname", "age", "direction_of_study", "phone", "post",
                    "admin_status"]
    if key in allowed_keys:
        query = f"UPDATE users SET {key} = ? WHERE username = ?"
        print(username, key, new_value)
        c.execute(query, (new_value, username))
        print()
        print(c.fetchall())

        conn.commit()
    else:
        raise ValueError(f"Некорректное имя поля: {key}")

    conn.close()


async def calculate_max_page():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Получаем количество пользователей
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    conn.close()

    # Рассчитываем максимальную страницу
    max_page = math.ceil(total_users / 5)  # Предполагая, что у вас по 5 пользователей на странице

    return max_page


async def add_news(text, date, recipients):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''INSERT INTO news (news_text, publish_date, recipients) VALUES (?, ?, ?)''',
              (text, date, recipients))
    conn.commit()
    conn.close()


async def read_news(date, chat_id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Получаем текущие данные из базы данных
    c.execute('''SELECT who_read FROM news WHERE publish_date = ?''', (date,))
    existing_who_read = c.fetchone()[0]
    print(existing_who_read)

    # Добавляем к текущим значениям нового пользователя
    if existing_who_read:
        new_who_read = existing_who_read + ', ' + str(chat_id)
    else:
        new_who_read = str(chat_id)

    # Обновляем запись в базе данных с новыми значениями
    c.execute('''UPDATE news SET who_read = ? WHERE publish_date = ?''', (new_who_read, date))

    conn.commit()
    conn.close()
