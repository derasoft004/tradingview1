import requests
import time

from config import URL_TG_BOT, CHAT_ID



def send_message(text):
    url = f"{URL_TG_BOT}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response.json()['result']['message_id']


def get_last_message(sent_message_id):
    print("Ожидание ответа...")
    while True:
        time.sleep(2)  # Задержка между запросами
        updates = get_updates()

        for update in updates:
            message = update.get('message')
            if message and message['chat']['id'] == CHAT_ID and message['message_id'] > sent_message_id:
                return message['text']


def get_updates():
    url = f"{URL_TG_BOT}/getUpdates"
    response = requests.get(url)
    updates = response.json()

    if updates['result']:
        return updates['result']
    return []


if __name__ == "__main__":
    # Отправляем сообщение
    sent_message = send_message("Привет! Ответь на это сообщение.")

    new_message = get_last_message(sent_message)

    # Ждем ответ
    print(new_message)

    print("Обработка завершена.")















