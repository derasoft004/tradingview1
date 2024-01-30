import pandas as pd
import datetime
import requests
import time
import random


FILE_SAVE_PATH = 'data_1_1h.csv'
PRICES_FILE_PATH = 'prices_save_file_1_1h.txt'
CURRENCY_RESULTS_FILE_PATH = 'saved_ratings_with_currency_1_1h.csv'

df = pd.read_csv(FILE_SAVE_PATH)

print(len(df[['MODE']]))
RESULTS = []


def make_request_link(symbol: str, open_normal_time, close_normal_time):
    response = requests.get(f'https://api.binance.com/api/v3/klines?symbol={symbol}'
                            f'&interval=1m&startTime={open_normal_time*1000}&endTime={close_normal_time*1000}')
    # print(response.json())
    return response.json()[0][4], response.json()[-1][4]


def separate_symbol_name(name: str) -> (str, str):
    name = name.replace('-', '')
    if 'USDT' in name:
        return name.replace('USDT', ''), 'USDT'
    elif 'USDC' in name:
        return name.replace('USDC', ''), 'USDC'
    elif 'USD' in name:
        return name.replace('USD', ''), 'USD'
    else: return None


df_times = df[['SYMBOL', 'TIME-OPEN', 'TIME-CLOSE']]
open_price_lst, close_price_lst = [], []
def make_prices_after_data():
    count = 0
    for elem in df_times.values:
        symbol, currency = separate_symbol_name(elem[0])

        lst_open = [int(t) for t in str(elem[1]).split(':')]
        open_normal_time = int(datetime.datetime(2024, 1, lst_open[0], lst_open[1], lst_open[2]).timestamp())
        lst_close = [int(t) for t in str(elem[2]).split(':')]
        close_normal_time = int(datetime.datetime(2024, 1, lst_close[0], lst_close[1], lst_close[2]).timestamp())
        print(open_normal_time, close_normal_time)

        try:
            opn, cls = make_request_link(symbol + currency, open_normal_time, close_normal_time)
            open_price_lst.append(opn)
            close_price_lst.append(cls)

            results_save_file = open(PRICES_FILE_PATH, 'a')
            if cls > opn:
                RESULTS.append(2)
                print(f'{symbol} {currency} : cls {cls} > opn {opn} {cls > opn}')
                results_save_file.write(f'{symbol} {currency} : cls {cls} > opn {opn} {cls > opn}, 2\n')
            elif cls == opn:
                RESULTS.append(0)
                print(f'{symbol} {currency} : cls {cls} == opn {opn} {cls == opn}')
                results_save_file.write(f'{symbol} {currency} : cls {cls} == opn {opn} {cls == opn}, 0\n')
            elif cls < opn:
                RESULTS.append(1)
                print(f'{symbol} {currency} : cls {cls} < opn {opn} {cls < opn}')
                results_save_file.write(f'{symbol} {currency} : cls {cls} < opn {opn} {cls < opn}, 1\n')

        except Exception as e:
            print(e)
            RESULTS.append(None)
            open_price_lst.append(None)
            close_price_lst.append(None)
        time.sleep(random.random())
        count += 1

        if not (count % 10):
            print(len(RESULTS), RESULTS)

# make_prices_after_data()


lst_currency, res_tmp = [], []
df_predicts = df[['MODE']]
def process_txt_file():
    file = open(PRICES_FILE_PATH, 'r')
    for line in file.readlines():
        # print('---', line.split()[-1].replace('\n', ''), sep='') # results
        res_tmp.append(line.split(', ')[-1].replace('\n', ''))
        open_price_lst.append(line.split()[7])
        close_price_lst.append(line.split()[4])
    print("len(df['PRICE-OPEN']): ", len(df['PRICE-OPEN']), "len(df['PRICE-CLOSE']): ", len(df['PRICE-CLOSE']),
          "\nlen(open_price_lst): ", len(open_price_lst), "len(close_price_lst): ", len(close_price_lst))
    df['PRICE-OPEN'] = open_price_lst
    df['PRICE-CLOSE'] = close_price_lst
    df['RESULT'] = res_tmp

process_txt_file()


# print(len(RESULTS), RESULTS)
# print(len(res_tmp), res_tmp)
# print('===========================================>', len(RESULTS) == len(res_tmp), ';', RESULTS == res_tmp, '\n')


def change_results():
    count = 0
    for elem in df_predicts.values:
        mode = elem
        value_count = int(res_tmp[count])
        if value_count not in (0, 1, 2):
            lst_currency.append(None)
        elif mode == 'long' and value_count == 2:
            lst_currency.append('True long')
        elif mode == 'short' and value_count == 1:
            lst_currency.append('True short')
        elif value_count == 0:
            lst_currency.append('False 0')
        elif mode == 'short' and value_count == 2:
            lst_currency.append('False short miss')
        elif mode == 'long' and value_count == 1:
            lst_currency.append('False long miss')
        else:
            lst_currency.append(None)
        count += 1

    # print(len(df['CONFIRMATION']), '==', len(lst_currency))
    df['CONFIRMATION'] = lst_currency
    print(df)

    df.to_csv(CURRENCY_RESULTS_FILE_PATH)

    print(df['CONFIRMATION'].value_counts())
    print(df['MODE'].value_counts())

change_results()













































