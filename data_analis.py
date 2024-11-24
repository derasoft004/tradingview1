import pandas as pd
from datetime import datetime
import requests

DATA_DF = pd.read_csv('data_forecasts.csv')

def request_binance(symbol: str, open_time: datetime, close_time: datetime, interval: str = '1h') -> str:
    """
    link binance api: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/public-api-endpoints#klinecandlestick-data

    lnk1 = request_binance('BTCUSDT')
    ' response structure
    [
      [
        1499040000000,      // Kline open time
        "0.01634790",       // Open price
        "0.80000000",       // High price
        "0.01575800",       // Low price
        "0.01577100",       // Close price
        "148976.11427815",  // Volume
        1499644799999,      // Kline Close time
        "2434.19055334",    // Quote asset volume
        308,                // Number of trades
        "1756.87402397",    // Taker buy base asset volume
        "28.46694368",      // Taker buy quote asset volume
        "0"                 // Unused field, ignore.
      ]
    ]
    '
    :param symbol:
    :param open_time:
    :param close_time:
    :param interval: minutes	1m, 3m, 5m, 15m, 30m
                     hours	 1h, 2h, 4h, 6h, 8h, 12h
                     days	 1d, 3d
    :return:
    """
    open_normal_time = int(open_time.timestamp() * 1000)
    close_normal_time = int(close_time.timestamp() * 1000)
    return f'https://api.binance.com/api/v3/klines?symbol={symbol}' \
           f'&interval={interval}&startTime={open_normal_time}&endTime={close_normal_time}'


def request_binance_one_time(symbol: str, target_time: datetime) -> str:
    target_time_ms = int(target_time.timestamp() * 1000)
    return f'https://api.binance.com/api/v3/klines?symbol={symbol}' \
           f'&interval=1m&startTime={target_time_ms}&endTime={target_time_ms}'


def get_open_prices(df: pd.DataFrame) -> list:
    symbols, times = df['SYMBOL'], df['TIME-OPEN']
    open_prices_lst = []

    for i in range(len(symbols)):
        symbol = symbols[i]

        date_time_str = times[i].split('.')[0]
        date_time_format = '%Y-%m-%d %H:%M:%S'
        date_time_obj = datetime.strptime(date_time_str, date_time_format).replace(second=0)

        link1 = request_binance_one_time(symbol, date_time_obj)
        response = requests.get(link1)
        r_obj = response.json()

        price_close = r_obj[0][1]
        open_prices_lst.append(price_close)
        print(symbol, 'time open:', date_time_obj, 'price open:', price_close)
    return open_prices_lst


def add_open_price_column() -> None:
    open_prices = get_open_prices(DATA_DF)
    DATA_DF['PRICE-OPEN'] = open_prices
    DATA_DF.to_csv('data_forecasts_price_open.csv')


def get_symbol_prices_in_interval(symbol: str, open_time: datetime, close_time: datetime) -> dict:
    interval = '1m'
    prices_in_interval_lst = {}

    prices_link = request_binance(symbol, open_time, close_time, interval)
    response = requests.get(prices_link)
    full_interval_data = response.json()
    for data_lst in full_interval_data:
        prices_dict = {
            'open_price': data_lst[1],
            'high_price': data_lst[2],
            'low_price': data_lst[3],
            'close_price': data_lst[4],

        }
        cur_time_prices = datetime.fromtimestamp(data_lst[0] / 1000)
        prices_in_interval_lst[cur_time_prices] = prices_dict

    return prices_in_interval_lst



def get_max_and_min_price():

    trg_time1 = datetime(2024, 11, 24, 15, 10)
    trg_time2 = datetime(2024, 11, 24, 15, 20)

    prices_dictionary = get_symbol_prices_in_interval('BTCUSDT', trg_time1, trg_time2)
    for time_, prices in prices_dictionary.items():
        pass






