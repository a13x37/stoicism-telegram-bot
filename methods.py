import requests
import datetime
import os

import psycopg2
from bs4 import BeautifulSoup as Soup


DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']


class BotHandler():

    def __init__(self, token):
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def send_message(
            self,
            chat_id,
            text,
            parse_mode=None,
            disable_web_page_preview=None,
            reply_markup=None):
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
            'reply_markup': reply_markup
            }
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def remove_webhook(self, drop_updates: bool = None):
        method = 'deleteWebhook'
        params = {'drop_pending_updates': drop_updates}
        resp = requests.post(self.api_url + method, params)
        return resp

    def set_webhook(self, url: str):
        method = 'setWebhook'
        params = {'url': url}
        resp = requests.post(self.api_url + method, params)
        return resp

    def getWebhookInfo(self):
        method = 'getWebhookInfo'
        resp = requests.get(self.api_url + method)
        webhookinfo = resp.json()
        return webhookinfo


class Db():

    dt = datetime.datetime.now()

    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
                )
        return self.connection

    def init_users_table(self, force: bool = False):
        ''' Проверяем, есть ли таблица. Если нет, таблица создаётся
            force: пересоздать таблицу
        '''
        conn = self.get_connection()
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

    def check_user(self, chat_id: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT chat_id FROM users WHERE chat_id = %s;", (chat_id,))
        data = c.fetchone()
        if data is None:
            return False
        else:
            return True

    def add_user(
            self,
            chat_id: int,
            last_seen,
            first_name: str = None,
            last_name: str = None,
            username: str = None,
            language_code: str = None,
            subscription: bool = False):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            '''
            INSERT INTO users(chat_id, first_name, last_name,
                            username, language_code, subscription, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (chat_id, first_name, last_name, username, language_code, subscription, last_seen)
        )
        conn.commit()

    def subscription_check(self, chat_id: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT subscription FROM users WHERE chat_id = %s", (chat_id,))
        data = c.fetchone()[0]
        if data == 1:
            return True
        else:
            return False

    def subscribe_user(self, subscription: bool, chat_id: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE users SET subscription = %s WHERE chat_id = %s",
            (subscription, chat_id)
        )
        conn.commit()

    def select_subscribers(self):
        data = []
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT chat_id FROM users WHERE subscription = %s", (True,))
        for user in c.fetchall():
            data.append(user[0])
        return data

    def update_last_seen(self, chat_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE users SET last_seen = %s WHERE chat_id = %s",
            (self.dt, chat_id)
        )
        conn.commit()

    def last_seen_today(self, chat_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT last_seen FROM users WHERE chat_id = %s", (chat_id,))
        output_data = c.fetchone()[0]
        if datetime.datetime.date(self.dt) == datetime.datetime.date(output_data):
            return True

    def init_quotes_table(self, force: bool = False):
        ''' Проверяем, есть ли таблица. Если нет, таблица создаётся
            force: пересоздать таблицу
        '''
        conn = self.get_connection()
        c = conn.cursor()

        if force is True:
            c.execute("DROP TABLE IF EXISTS quotes")

        c.execute('''
                CREATE TABLE IF NOT EXISTS quotes(
                    id              SERIAL NOT NULL PRIMARY KEY,
                    quote           TEXT,
                    author          TEXT
                )
                ''')
        conn.commit()

    def get_random_quote(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT quote, author FROM quotes ORDER BY RANDOM() LIMIT 1")
        data = c.fetchone()
        return data


url = "https://jegornagel.com/stoic/"


def parser_page():
    articles_list = ''
    counter = 0
    html = requests.get(url)
    soup = Soup(html.text, 'html.parser')
    articles = soup.find(
        'ul', class_='wp-block-latest-posts__list is-style-default tw-heading-size-medium wp-block-latest-posts').find_all('a')
    for article in articles:
        counter += 1
        articles_list += "{}. [{}]({}) \n".format(counter, article.get_text(), article.get('href'))
    return articles_list


if __name__ == '__main__':
    db = Db()
    db.get_connection()
    # db.init_quotes_table(force=True)
    # print(db.get_random_quote())
