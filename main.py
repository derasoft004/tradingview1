from tradingview_ta import TA_Handler, Interval, Exchange
from binance.um_futures import UMFutures
import time
import datetime
import requests
import csv
import os


INTERVAL = Interval.INTERVAL_1_MINUTE

TELEGRAM_TOKEN = '6813749013:AAHMwGHqaCpC72ttA-WGdLJyvETXRAYpeb4'
TELEGRAM_CHANNEL = '@tradingviewname1_bot'
URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'

# print(requests.get(URL + '/getUpdates').json()) # выясняем ID чата
ID = 1191242436

FILE_SAVE_PATH = 'data_4_1m.csv'

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
    return longs, shorts


def make_time_close_days(time_now_tmp) -> str:
    time_close_tmp = int(str(time_now_tmp).split(':')[1])
    if 0 <= time_close_tmp < 30:
        time_close_tmp = time_close_tmp + 1
    elif time_close_tmp == 30:
        time_close_tmp = 1
    return time_now_tmp.replace(time_now_tmp.split(':')[1], str(time_close_tmp))


def make_time_close_hours(time_now_tmp) -> str:
    time_close_tmp = int(str(time_now_tmp).split(':')[2])
    if 0 <= time_close_tmp < 23:
        time_close_tmp = time_close_tmp + 1
    elif time_close_tmp == 23:
        time_close_tmp = 0
        time_now_tmp = make_time_close_days(time_now_tmp)
    return time_now_tmp.replace(time_now_tmp.split(':')[2], str(time_close_tmp))


def make_time_close_minutes(time_now_tmp) -> str:
    time_close_tmp = int(str(time_now_tmp).split(':')[3])
    if 0 <= time_close_tmp < 59:
        time_close_tmp = time_close_tmp + 1
    elif time_close_tmp == 59:
        time_close_tmp = 0
        time_now_tmp = make_time_close_hours(time_now_tmp)
    return time_now_tmp.replace(time_now_tmp.split(':')[3], str(time_close_tmp))

if not os.path.exists(FILE_SAVE_PATH):
    with open(FILE_SAVE_PATH, 'w') as csvfile:
        writer_head = csv.DictWriter(csvfile, fieldnames=['MODE', 'SYMBOL', 'TIME-OPEN', 'PRICE-OPEN', 'TIME-CLOSE',
                                                          'PRICE-CLOSE', 'RESULT', 'CONFIRMATION'])
        writer_head.writeheader()
        print(f'file {FILE_SAVE_PATH} is created.\n')


print('START')
first_data()


def main():
    main_flag = True
    symbol_times = []
    count_predicts, count_loops = 0, 1
    while main_flag:
        print('====================NEW ROUND===================')
        for i in symbols:
            try:
                time_now = datetime.datetime.now()
                data = get_data(i)
                print('==========', i, data, '==========', sep='=====')
                time_now_tmp = f'{time_now.month}:{time_now.day}:{time_now.hour}:{time_now.minute}:{time_now.second}'
                symbol = data['SYMBOL']
                # symbol_name, currency = separate_symbol_name(symbol)

                if data['RECOMMENDATION'] == 'STRONG_BUY' and symbol not in longs and int(data['NEUTRAL']) <= 8:
                    send_message(f'{symbol} + BUY\nCOUNT: {count_predicts}\nNEUTRAL: {data["NEUTRAL"]}\nBUY: '
                                 f'{data["BUY"]}\nSELL: {data["SELL"]}')
                    with open(FILE_SAVE_PATH, 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        time_close_tmp = make_time_close_minutes(time_now_tmp)
                        writer.writerow(['long', symbol, time_now_tmp, None, time_close_tmp, None, None, None])
                    longs.append(symbol)
                    symbol_times.append((symbol, time_now_tmp))
                    count_predicts += 1
                    time.sleep(0.1)

                if data['RECOMMENDATION'] == 'STRONG_SELL' and symbol not in shorts and int(data['NEUTRAL']) <= 8:
                    send_message(f'{symbol} + SELL\nCOUNT: {count_predicts}\nNEUTRAL: {data["NEUTRAL"]}\nBUY: '
                                 f'{data["BUY"]}\nSELL: {data["SELL"]}')
                    with open(FILE_SAVE_PATH, 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        time_close_tmp = make_time_close_minutes(time_now_tmp)
                        writer.writerow(['short', symbol, time_now_tmp, None, time_close_tmp, None, None, None])
                    shorts.append(symbol)
                    symbol_times.append((symbol, time_now_tmp))
                    count_predicts += 1
                    time.sleep(0.1)

                if not (count_predicts % 100): print(count_predicts)
                if count_predicts == 10000: main_flag = False
            except:
                pass

        if not (count_loops % 3):
            print(f'{longs},\n{shorts},\nare cleared, count_loops = {count_loops}\n')
            longs.clear()
            shorts.clear()
        count_loops += 1


main()





















