import requests

from config import ID, URL_TG_BOT

def send_message(message):
    URL_MESSAGE = URL_TG_BOT + f'/sendMessage?chat_id={ID}&text={message}!'
    requests.get(URL_MESSAGE) # отсылаем сообщение
