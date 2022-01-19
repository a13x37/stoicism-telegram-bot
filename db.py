import psycopg2
import datetime
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


__connection = None


def get_connection():
    global __connection
    if __connection is None:
        __connection = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
            )
    return __connection


def init_db(force: bool = False):
    ''' Проверяем, есть ли таблица. Если нет, таблица создаётся
        force: пересоздать таблицу
    '''
    conn = get_connection()
    c = conn.cursor()

    if force is True:
        c.execute("DROP TABLE IF EXISTS users")

    c.execute('''
              CREATE TABLE IF NOT EXISTS users(
                id              SERIAL NOT NULL PRIMARY KEY,
                chat_id         INTEGER NOT NULL UNIQUE,
                first_name      TEXT,
                last_name       TEXT,
                username        TEXT,
                language_code   TEXT,
                subscription    BOOLEAN,
                last_seen       TIMESTAMP
              )
              ''')
    conn.commit()


def check_user(chat_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT chat_id FROM users WHERE chat_id = %s;", (chat_id,))
    data = c.fetchone()
    if data is None:
        return False
    else:
        return True


def add_user(
        chat_id: int,
        last_seen,
        first_name: str = None,
        last_name: str = None,
        username: str = None,
        language_code: str = None,
        subscription: bool = False):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        '''
        INSERT INTO users(chat_id, first_name, last_name,
                          username, language_code, subscription, last_seen)
        VALUES (%s, %s, %s, %s, %s, %s, %s)''',
        (chat_id, first_name, last_name, username, language_code, subscription, last_seen)
    )
    conn.commit()


def subscription_check(chat_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT subscription FROM users WHERE chat_id = %s", (chat_id,))
    data = c.fetchone()[0]
    if data == 1:
        return True
    else:
        return False


def subscribe_user(subscription: bool, chat_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET subscription = %s WHERE chat_id = %s",
        (subscription, chat_id)
    )
    conn.commit()


def select_subscribers():
    data = []
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT chat_id FROM users WHERE subscription = %s", (True,))
    for user in c.fetchall():
        data.append(user[0])
    return data


def update_last_seen(seen_datetime, chat_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET last_seen = %s WHERE chat_id = %s",
        (seen_datetime, chat_id)
    )
    conn.commit()


dt = datetime.datetime.now()


def last_seen_today(chat_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT last_seen FROM users WHERE chat_id = %s", (chat_id,))
    output_data = c.fetchone()[0]
    if datetime.datetime.date(dt) == datetime.datetime.date(output_data):
        return True


if __name__ == '__main__':
    get_connection()
    # init_db(force=True)
