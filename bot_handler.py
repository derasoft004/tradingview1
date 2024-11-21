import requests

from config import ID, TELEGRAM_TOKEN, TELEGRAM_CHANNEL, URL

def send_message(message):
    URL_MESSAGE = URL + f'/sendMessage?chat_id={ID}&text={message}!'
    requests.get(URL_MESSAGE) # отсылаем сообщение