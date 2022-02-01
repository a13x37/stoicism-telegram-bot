import os
import json
import time
import datetime
import threading
import traceback

import schedule
from flask import Flask, request

from methods import BotHandler, Db, parser_page
from handler import start, menu, start_keyboard, phrase_request_keyboard, about_keyboard, articles_keyboard


BOT_TOKEN = os.environ['TOKEN']
APP_URL = os.environ['APP_URL'] + BOT_TOKEN

bot = BotHandler(BOT_TOKEN)
db = Db()


server = Flask(__name__)
# server.config['DEBUG'] = True

dt = datetime.datetime.now()


@server.route('/')
def say_hello():
    return "Hello, user!"


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def mailing():
    for user in db.select_subscribers():
        bot.send_message(
            chat_id=user,
            text=phrase_request(),
            parse_mode="Markdown",
        )


schedule.every().day.at("07:00").do(mailing)

# Start the background thread
stop_run_continuously = run_continuously()


def phrase_request():
    data = db.get_random_quote()
    phrase = "{} \n*{}*".format(data[0], data[1])
    return phrase


offset = 0


def offset_check(update_id):
    global offset
    if update_id > offset:
        offset = update_id
    else:
        raise ValueError("Запрос с этим update_id уже был отработан")


def json_parse(json):
    update_dict = {}
    update_dict['update_id'] = json['update_id']
    update_dict['chat_id'] = json['message']['chat']['id']
    update_dict['text'] = json['message']['text']
    update_dict['first_name'] = json['message']['from'].get('first_name')
    update_dict['last_name'] = json['message']['from'].get('last_name')
    update_dict['username'] = json['message']['from'].get('username')
    update_dict['language_code'] = json['message']['from'].get('language_code')
    return update_dict


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def main():
    sub_check = None
    try:
        json_str = request.get_json()
        update = json_parse(json_str)
        offset_check(update['update_id'])

        if db.check_user(update["chat_id"]) is False:
            db.add_user(
                chat_id=update['chat_id'],
                first_name=update['first_name'],
                last_name=update['last_name'],
                username=update['username'],
                language_code=update['language_code'],
                subscription=False,
                last_seen=dt
                )
            bot.send_message(
                chat_id=update['chat_id'],
                text=start(update['first_name']),
                parse_mode="Markdown")

        if update['text'] in ('/start', 'Меню'):
            sub_check = db.subscription_check(chat_id=update['chat_id'])
            if db.last_seen_today(update['chat_id']) is True:
                pass
            else:
                bot.send_message(
                    chat_id=update['chat_id'],
                    text=start(update['first_name']),
                    parse_mode="Markdown")
            bot.send_message(
                chat_id=update['chat_id'],
                text=menu(sub_check),
                parse_mode="Markdown",
                reply_markup=json.dumps(start_keyboard(sub_check))
            )
        elif update['text'] == 'Подписаться':
            sub_check = db.subscription_check(chat_id=update['chat_id'])
            if sub_check is True:
                message = "Подписка уже оформлена!"
            else:
                db.subscribe_user(not sub_check, update['chat_id'])
                message = "Подписка оформлена! Фразы будут приходить в 10:00."
            bot.send_message(
                chat_id=update['chat_id'],
                text=message,
                reply_markup=json.dumps(start_keyboard(True))
            )

        elif update['text'] == 'Отписаться':
            sub_check = db.subscription_check(chat_id=update['chat_id'])
            if sub_check is False:
                message = "Вы не были подписаны на рассылку."
            else:
                db.subscribe_user(not sub_check, update['chat_id'])
                message = "Вы отписаны от рассылки! Фразы больше не будут приходить."
            bot.send_message(
                chat_id=update['chat_id'],
                text=message,
                reply_markup=json.dumps(start_keyboard(False))
            )
        elif update['text'] in ('Фраза', 'Ещё!'):
            bot.send_message(
                chat_id=update['chat_id'],
                text=phrase_request(),
                parse_mode="Markdown",
                reply_markup=json.dumps(phrase_request_keyboard)
            )

        elif update['text'] == 'О философии стоицизма':
            sub_check = db.subscription_check(chat_id=update['chat_id'])
            bot.send_message(
                chat_id=update['chat_id'],
                text='https://jegornagel.com/sovremennyj-stoiczizm/',
                reply_markup=json.dumps(about_keyboard)
            )

        elif update['text'] == 'Сборник статей':
            bot.send_message(
                chat_id=update['chat_id'],
                text=parser_page(),
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=json.dumps(articles_keyboard)
            )

        db.update_last_seen(update['chat_id'])

    except Exception as e:
        print(e)
        traceback.print_exc()
        time.sleep(1)
    return "OK"


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
