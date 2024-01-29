'''
пока что отложим этот варик, не берутся истинные цены поминутно,
возможно стоит get_historical_price_minute


'''


import pandas as pd
import datetime
from cryptocompare import get_historical_price, get_historical_price_minute
# from main import separate_symbol_name
import requests
import time
import random

df = pd.read_csv('data.csv')
# print(df)

df_times = df[['SYMBOL', 'TIME-OPEN', 'TIME-CLOSE']]
# print(df_open_times)
print(len(df[['MODE']]))
RESULTS = []


def make_request_link(symbol: str, open_normal_time, close_normal_time):
    response = requests.get(f'https://api.binance.com/api/v3/klines?symbol={symbol}'
                            f'&interval=1m&startTime={open_normal_time*1000}&endTime={close_normal_time*1000}')
    return response.json()[0][4], response.json()[1][4]


def separate_symbol_name(name: str) -> (str, str):
    name = name.replace('-', '')
    if 'USDT' in name:
        return name.replace('USDT', ''), 'USDT'
    elif 'USDC' in name:
        return name.replace('USDC', ''), 'USDC'
    elif 'USD' in name:
        return name.replace('USD', ''), 'USD'
    else: return None


def make_costs_after_data():
    count = 0
    for elem in df_times.values:
        # print(elem)
        symbol, currency = separate_symbol_name(elem[0])

        lst_open = [int(t) for t in str(elem[1]).split(':')]
        open_normal_time = int(datetime.datetime(2024, 1, lst_open[0], lst_open[1], lst_open[2]).timestamp())
        lst_close = [int(t) for t in str(elem[2]).split(':')]
        close_normal_time = int(datetime.datetime(2024, 1, lst_close[0], lst_close[1], lst_close[2]).timestamp())
        print(open_normal_time, close_normal_time, datetime.datetime.now())
        opn, cls = make_request_link(symbol + currency, open_normal_time, close_normal_time)

        try:
            # opn = get_historical_price(symbol, currency, timestamp=open_normal_time)[symbol][currency]
            # cls = get_historical_price(symbol, currency, timestamp=close_normal_time)[symbol][currency]
            # nw = get_historical_price(symbol, currency, timestamp=datetime.datetime.now())[symbol][currency]
            RESULTS.append(cls > opn) # добавляется True или False, которые истинные для лонга (цена выросла)
            print(symbol, currency, ': cls ', cls, '>', 'opn ', opn, ' ', cls > opn, 'now: ')
            print(open_normal_time, close_normal_time)
            results_save_file = open('results_save_file.txt', 'a')
            results_save_file.write(f'{symbol}:  cls {cls} > opn {opn}, {cls > opn}, {str(RESULTS[count])}\n')
        except Exception as e:
            print(e)
            RESULTS.append(None)
        time.sleep(random.random()*2)
        count += 1

        if not (count % 10):
            print(len(RESULTS), RESULTS)
# make_costs_after_data()


df_predicts = df[['MODE']]
lst_currency, res_tmp = [], []
file = open('results_save_file.txt', 'r')
for line in file.readlines():
    res_tmp.append(line.split(', ')[-1].replace('\n', ''))

def change_results():
    count = 0
    for elem in df_predicts.values:
        mode = elem
        # if res_tmp[count] not in (True, False):
        #     lst_currency.append(None)
        if mode == 'long' and res_tmp[count]:
            lst_currency.append(True)
        elif mode == 'short' and not res_tmp[count]:
            lst_currency.append(True)
        else:
            lst_currency.append(False)
        count += 1

change_results()


print(len(df['RESULT']), '==', len(lst_currency))
df['RESULT'] = lst_currency
print(df)

df.to_csv('saved_ratings_with_currency.csv')

print(df['RESULT'].value_counts())











































