from tradingview_ta import TA_Handler, Interval, Exchange
from binance.um_futures import UMFutures
import time
import datetime
import requests
import cryptocompare
import csv

# https://pypi.org/project/cryptocompare/
# print(cryptocompare.get_coin_list(format=True)) # coin_list
# print(cryptocompare.get_price('BTC', 'USD')) # what is BTC price in USD
# cryptocompare.get_price(['BTC', 'ETH'], ['EUR', 'GBP'])
# print(cryptocompare.get_historical_price('BTC', 'EUR', datetime.datetime(2017,6,6))) # history cost
# print(cryptocompare.get_historical_price_hour('BTC', currency='EUR', limit=1))

# print(cryptocompare.get_price('GFY'))


INTERVAL = Interval.INTERVAL_1_MINUTE

TELEGRAM_TOKEN = '6813749013:AAHMwGHqaCpC72ttA-WGdLJyvETXRAYpeb4'
TELEGRAM_CHANNEL = '@tradingviewname1_bot'
URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'

# print(requests.get(URL + '/getUpdates').json()) # выясняем ID чата
ID = 1191242436


def send_message(message):
    URL_MESSAGE = URL + f'/sendMessage?chat_id={ID}&text={message}!'
    requests.get(URL_MESSAGE) # отсылаем сообщение


client = UMFutures()

def get_data(symbol):
    output = TA_Handler(
        symbol=symbol,
        screener='Crypto',
        exchange='Binance',
        interval=INTERVAL
    )
    activiti = output.get_analysis().summary
    # print('activiti is: ', activiti)
    activiti['SYMBOL'] = symbol
    return activiti


def get_symbols():
    tickers = client.mark_price()
    symbols = []
    for element in tickers:
        ticker = element['symbol']
        symbols.append(ticker)
    return symbols


symbols = get_symbols()
longs, shorts = [], []


def separate_symbol_name(name: str) -> (str, str):
    name = name.replace('-', '')
    if 'USDT' in name:
        return name.replace('USDT', ''), 'USDT'
    elif 'USDC' in name:
        return name.replace('USDC', ''), 'USDC'
    elif 'USD' in name:
        return name.replace('USD', ''), 'USD'
    else: return None

def first_data():
    # print('Search first data')
    for i in symbols:
        try:
            data = get_data(i)
            if data['RECOMMENDATION'] == 'STRONG_BUY':
                longs.append(data['SYMBOL'])

            if data['RECOMMENDATION'] == 'STRONG_SELL':
                shorts.append(data['SYMBOL'])
            time.sleep(0.01)
        except:
            pass
            # print('first_data error')
    # print('longs: ', longs, '\nshorts: ', shorts)
    return longs, shorts


def make_time_close_days(time_now_tmp):
    time_close_tmp = int(time_now_tmp.split(':')[0])
    if 0 <= time_close_tmp < 30:
        if len(str(time_close_tmp + 1)) == 2:
            time_close_tmp = str(time_close_tmp + 1)
        else: time_close_tmp = '0' + str(time_close_tmp + 1)
    else:
        time_close_tmp = '01'
    return time_now_tmp.replace(time_now_tmp.split(':')[0], time_close_tmp)


def make_time_close_hours(time_now_tmp):
    time_close_tmp = int(time_now_tmp.split(':')[1])
    if 0 <= time_close_tmp < 23:
        if len(str(time_close_tmp + 1)) == 2:
            time_close_tmp = str(time_close_tmp + 1)
        else: time_close_tmp = '0' + str(time_close_tmp + 1)
    else:
        time_close_tmp = '00'
        time_now_tmp = make_time_close_days(str(time_now_tmp))
    return time_now_tmp.replace(time_now_tmp.split(':')[1], time_close_tmp)


def make_time_close_minutes(time_now_tmp):
    time_close_tmp = int(time_now_tmp.split(':')[2])
    if 0 <= time_close_tmp < 59:
        if len(str(time_close_tmp + 1)) == 2:
            time_close_tmp = str(time_close_tmp + 1)
        else: time_close_tmp = '0' + str(time_close_tmp + 1)
    else:
        time_close_tmp = '00'
        time_now_tmp = make_time_close_hours(str(time_now_tmp))
    return time_now_tmp.replace(time_now_tmp.split(':')[2], time_close_tmp)


with open('data_10000_1m.csv', 'w') as csvfile:
    writer_head = csv.DictWriter(csvfile, fieldnames=['MODE', 'SYMBOL', 'TIME-OPEN', 'PRICE-OPEN', 'TIME-CLOSE',
                                                      'PRICE-CLOSE', 'RESULT'])
    writer_head.writeheader()


print('START')
first_data()


count_predicts = 0
symbol_times = []
main_flag = True
while main_flag:
    print('====================NEW ROUND===================')
    for i in symbols:
        try:
            time_now = datetime.datetime.now()
            data = get_data(i)
            time_now_tmp = f'{time_now.day}:{time_now.hour}:{time_now.minute}:{time_now.second}'
            symbol = data['SYMBOL']
            symbol_name, currency = separate_symbol_name(symbol)
            # print(cryptocompare.get_price(symbol_name, currency))
            # print(cryptocompare.get_historical_price(symbol, timestamp=time_now))


            if data['RECOMMENDATION'] == 'STRONG_BUY' and symbol not in longs:
                # send_message(symbol + ' BUY')
                with open('data_10000_1m.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    time_close_tmp = make_time_close_minutes(time_now_tmp)
                    writer.writerow(['long', symbol, time_now_tmp, None, time_close_tmp, None, None])
                longs.append(symbol)
                symbol_times.append((symbol, time_now_tmp))
                count_predicts += 1

            if data['RECOMMENDATION'] == 'STRONG_SELL' and symbol not in shorts:
                # send_message(symbol + ' SELL')
                with open('data_10000_1m.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    time_close_tmp = make_time_close_minutes(time_now_tmp)
                    writer.writerow(['short', symbol, time_now_tmp, None, time_close_tmp, None, None])
                shorts.append(symbol)
                symbol_times.append((symbol, time_now_tmp))
                count_predicts += 1

            time.sleep(0.1)
            if not (count_predicts % 100): print(count_predicts)
            if count_predicts == 10000: main_flag = False
            """
            следующий шаг:
            сформировать датасет
            подключить пандас
            по данным времени с помощью датасета сделать обьект datetime
            проставить True и False
            провести статистику
            """
            # for elem in symbol_times:
            #     symbol, time_start_tmp = elem
            #     if time_start_tmp == make_time_close_minutes(time_start_tmp):
            #
            #             symbol_times.remove(elem)

        except:
            pass






















