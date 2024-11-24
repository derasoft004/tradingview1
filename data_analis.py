import pandas as pd
from datetime import datetime
import requests
from config import FILE_DATA_PATH, FILE_DATA_PRICE_OPEN_PATH

DATA_DF = pd.read_csv(FILE_DATA_PATH)

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


def add_some_column(file_name: str, column_name: str, data) -> None:
    DATA_DF[column_name] = data
    DATA_DF.to_csv(file_name)


def get_symbol_prices_in_interval(symbol: str, open_time: datetime, close_time: datetime) -> dict:
    interval = '1m'
    prices_in_interval_dict = {}

    prices_link = request_binance(symbol, open_time, close_time, interval)
    response = requests.get(prices_link)
    full_interval_data = response.json()
    for data_to_min in full_interval_data:
        prices_dict = {
            'open_price': float(data_to_min[1]),
            'high_price': float(data_to_min[2]),
            'low_price': float(data_to_min[3]),
            'close_price': float(data_to_min[4]),

        }
        cur_time_prices = datetime.fromtimestamp(data_to_min[0] / 1000)
        prices_in_interval_dict[cur_time_prices] = prices_dict

    return prices_in_interval_dict



def get_max_and_min_price():

    trg_time1 = datetime(2024, 11, 24, 15, 10)
    trg_time2 = datetime(2024, 11, 24, 15, 30)

    prices_dictionary = get_symbol_prices_in_interval('BTCUSDT', trg_time1, trg_time2)
    max_price, min_price = 0, 999999999999999999
    for time_, prices in prices_dictionary.items():
        if prices['high_price'] > max_price:
            max_price = prices['high_price']
        if prices['low_price'] < min_price:
            min_price = prices['low_price']

    return max_price, min_price


def check_changing_in_interval(mode: str, symbol: str, open_price: float, open_time: datetime, close_time: datetime):
    prices_dictionary = get_symbol_prices_in_interval(symbol, open_time, close_time)
    one_percent = open_price / 100
    print(f"Symbol: {symbol}")
    if mode == 'long':
        long_price_prof = open_price + one_percent * 5
        close_price = open_price - one_percent * 3
        print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: {one_percent}\nlong_price_prof: {long_price_prof}\nclose_price: {close_price}")
        for time_, prices in prices_dictionary.items():
            max_price_minute = prices['high_price']
            min_price_minute = prices['low_price']
            if max_price_minute >= long_price_prof: # в интервале лонг прогнозирован правильно
                print('time win:', time_, max_price_minute)
                return 1
            elif min_price_minute <= close_price: # в интервале лонг прогнозирован неправильно
                print('time los:', time_, min_price_minute)
                return -1

    elif mode == 'short':
        short_price_prof = open_price - one_percent * 5
        close_price = open_price + one_percent * 3
        print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: {one_percent}\nshort_price_prof: {short_price_prof}\nclose_price: {close_price}")

        for time_, prices in prices_dictionary.items():
            max_price_minute = prices['high_price']
            min_price_minute = prices['low_price']
            if min_price_minute <= short_price_prof: # в интервале шорт прогнозирован правильно
                print('time win:', time_, max_price_minute)
                return 1
            elif max_price_minute >= close_price: # в интервале шорт прогнозирован неправильно
                print('time los:', time_, min_price_minute)
                return -1

    return 0


# trg_time1 = datetime(2024, 11, 24, 12, 7)
# trg_time2 = datetime(2024, 11, 24, 16, 1)

# print(check_changing_in_interval('short', 'LINKUSDT', 17.8224, trg_time1, trg_time2))

def check_data_forecasts():
    # lst_open_prices = get_open_prices(DATA_DF)
    # add_some_column(FILE_DATA_PRICE_OPEN_PATH, 'PRICE-OPEN', lst_open_prices)
    total_forecasts_dict = {"win": 0,
                            "los": 0}
    DATA_DF_OPEN_PRICE = pd.read_csv(FILE_DATA_PRICE_OPEN_PATH)

    for row in DATA_DF_OPEN_PRICE.itertuples(index=False):
        mode = row.MODE
        symbol = row.SYMBOL
        time_open = row[5].split('.')[0]
        price_open = row[6]

        time_open_datetime = datetime.strptime(time_open, '%Y-%m-%d %H:%M:%S').replace(second=0)
        time_now = datetime.now()

        res = check_changing_in_interval(mode, symbol, price_open, time_open_datetime, time_now)
        if res == 1:
            total_forecasts_dict["win"] += 1
        if res == -1:
            total_forecasts_dict["los"] += 1
    total_sum = total_forecasts_dict["win"] + total_forecasts_dict["los"]
    print(f"Forecasts count: {len(DATA_DF_OPEN_PRICE)}\n"
          f"Correctness of forecasts: {total_forecasts_dict}\n"
          f"Total sum: {total_sum}")

check_data_forecasts()






