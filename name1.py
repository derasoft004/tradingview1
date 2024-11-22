# '''
# рабочий метод получения по запросу к апи бинанс
#
# '''
#
# import requests
# import datetime
#
# # Указываем символ THETA и валюту USDT
# symbol = 'THETAUSDT'
#
# # Указываем временную метку в формате Unix timestamp (например, для 13:22 сегодняшнего дня)
# open_normal_time = int(datetime.datetime(2024, 1, 29, 13, 22).timestamp())
# close_normal_time = int(datetime.datetime(2024, 1, 29, 13, 24).timestamp())
# print(open_normal_time)
#   # Пример временной метки для 13:22 сегодняшнего дня
#
# # Отправляем запрос к API биржи Binance для получения исторической цены
# def make_request_link(symbol: str, open_normal_time, close_normal_time):
#     response = requests.get(f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&startTime={open_normal_time*1000}&endTime={close_normal_time*1000}')
#     return response.json()[0][4], response.json()[1][4]
#
# data = make_request_link(symbol, open_normal_time, close_normal_time)
# print(data)
# Извлекаем цену из полученных данных
# price = float(data[0][4])  # Цена закрытия свечи за указанное время
# price1 = float(data[2][4])  # Цена закрытия свечи за указанное время
#
# print(f"Цена THETA в USDT в 13:22 сегодняшнего дня: {data}")
# print(f"Цена THETA в USDT в 13:23 сегодняшнего дня: {price1}")
#
# print(f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&startTime={open_normal_time*1000}&endTime={close_normal_time*1000}')

# import pandas as pd
#
# df = pd.DataFrame([[1,'Bob', 'Builder'],
#                   [2,'Sally', 'Baker'],
#                   [3,'Scott', 'Candle Stick Maker']],
#                   columns=['id','name', 'occupation'])
# df['id'] = [0, 0, 0]
# print(df)

# file = open('data_3_1h.csv', 'r')
# new_file = open('data_3_1h.csv', 'w')
#
# for line in file.readlines():
#     if len(line) > 1: new_file.write(line)









