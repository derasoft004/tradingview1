import requests
import time

from config import CHAT_ID, URL_TG_BOT, FILE_CHAT_IDS_PATH, CHAT_ID_KEEMQQ


def send_message(chat_id: int, message: str, keyboard_flag: bool = False, keyboard: list = []):
    url = URL_TG_BOT + '/sendMessage'

    params = {
        'chat_id': chat_id,
        'text': message
    }
    if keyboard_flag:
        params['reply_markup'] = {
            'keyboard': [
                keyboard
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }

    requests.post(url, json=params)

    url_to_update_id = URL_TG_BOT + '/getUpdates'
    response_to_update_id = requests.get(url_to_update_id)

    updates = response_to_update_id.json().get('result', [])
    if updates:
        last_update = updates[-1]
        update_id = last_update.get('update_id')
        return update_id
    return None


def get_chat_id():
    url = URL_TG_BOT + '/getUpdates'

    response = requests.get(url)

    updates = response.json()['result']
    last_update = updates[-1]
    message = last_update.get('message')
    print(message)
    return message['chat']['id']


def get_chat_ids_list() -> list:
    with open(FILE_CHAT_IDS_PATH, 'r') as file:
        return file.readline().split(',')


def get_message(pre_message_id, chat_id: int | str) -> str:
    """
        перед тем как прочитать новое сообщение получаем АЙДИ последнего сообщения из функции send_message
         и проверяем до тех пор пока последнее сообщение из updates не будет не равно тому что пришло
    """
    url = URL_TG_BOT + '/getUpdates'

    while True:
        response = requests.get(url)
        updates = response.json().get('result', [])

        if updates:
            last_update = updates[-1]
            now_message_id = last_update.get('update_id')

            if pre_message_id != now_message_id:
                message = last_update.get('message')
                if message and message['chat']['id'] == chat_id:
                    first_name = message['chat'].get('first_name', 'Unknown')
                    username = message['chat'].get('username', 'Unknown')
                    text = message['text']
                    return f"Получено сообщение от {first_name} (@{username}): {text}"

        time.sleep(1)  # Задержка для предотвращения частых запросов


while True:
    last_update_id = send_message(CHAT_ID, 'hello', True, ['hi', 'bay'])
    print(last_update_id)
    received_message = get_message(last_update_id, CHAT_ID)
    print(received_message)
    time.sleep(2)  # Задержка между отправками сообщений
# print(get_chat_id())
# buttons = [
#     {'text': 'hi'},
#     {'text': 'bay'}
# ]
# send_message(CHAT_ID_KEEMQQ, 'нюхай жопу', True, buttons)
















