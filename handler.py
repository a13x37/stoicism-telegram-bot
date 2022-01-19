import datetime


now = datetime.datetime.now()
today = now.day
hour = now.hour


def menu(sub_check: bool):
    if sub_check is True:
        return '''
        \nЧтобы получить цитату философа, нажмите *"Фраза"*.
        \nДля отказа от ежедневной рассылки фраз, нажмите *"Отписаться"*.  Рассылка приходить больше не будет.
        \nЕсли хотите больше узнать о современном стоицизме, нажмите *"О философии стоицизма"*.
        '''
    else:
        return'''
        \nЧтобы получить цитату философа, нажмите *"Фраза"*.
        \nДля подписки на ежедневную рассылку фраз, нажмите *"Подписаться"*.  Рассылка приходит в *10:00* по Москве (GMT+3).
        \nЕсли хотите больше узнать о современном стоицизме, нажмите *"О философии стоицизма"*.
        '''


def start(name):
    if today == now.day and 6 <= hour < 12:
        return "Доброе утро, {}!".format(name)

    elif today == now.day and 12 <= hour < 17:
        return "Добрый день, {}!".format(name)

    elif today == now.day and 17 <= hour < 24:
        return "Добрый вечер, {}!".format(name)

    elif today == now.day and 0 <= hour < 6:
        return "Доброй ночи, {}!".format(name)


def start_keyboard(sub_check: bool):
    if sub_check is True:
        subText = 'Отписаться'
    else:
        subText = 'Подписаться'
    keyboard = {
        "keyboard": [
            [
                {"text": "Фраза"},
                {"text": subText}
            ],
            [
                {"text": "О философии стоицизма"}
            ]
        ],
        "resize_keyboard": True,
        # "one_time_keyboard": True
    }
    return keyboard


phrase_request_keyboard = {
    "keyboard": [
        [
            {"text": "Ещё!"},
            {"text": "Меню"}
        ],
        [
            {"text": "О философии стоицизма"}
        ]
    ],
    "resize_keyboard": True,
    # "one_time_keyboard": True
}

about_keyboard = {
    "keyboard": [
        [
            {"text": "Фраза"},
            {"text": "Меню"}
        ],
        [
            {"text": "Сборник статей"}
        ]
    ],
    "resize_keyboard": True,
    # "one_time_keyboard": True
}

articles_keyboard = {
    "keyboard": [
        [
            {"text": "Меню"}
        ]
    ],
    "resize_keyboard": True,
    # "one_time_keyboard": True
}
