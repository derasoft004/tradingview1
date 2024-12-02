from math import log10

import pandas as pd
from datetime import datetime, timedelta
import requests
from config import (API_URL_BYBIT, FILE_DATA_PATH_WITH_SOME_CONFIRMATION,
                    FILE_DATA_PATH_WITH_SOME_CONFIRMATION_TP2_LS10,
                    FILE_DATA_PATH_WITH_SOME_CONFIRMATION_TP5_LS_AFTER24H_3, WAIT_HOURS, RANGE_TO_GET_ROWS)

DATA_DF = pd.read_csv(FILE_DATA_PATH_WITH_SOME_CONFIRMATION_TP5_LS_AFTER24H_3, index_col=0)


def get_res_for_kline_binance(symbol: str,
                              start_time: datetime,
                              end_time: datetime,
                              open_price: float,
                              mode: str,
                              wait_hours: bool
                              ) -> int:
    prices_in_interval_dict = {}

    url = f'https://api.binance.com/api/v3/klines'

    def get_prices(start_timestamp_, end_timestamp_, current_dict_: dict):
        # print('s:', datetime.fromtimestamp(int(start_timestamp_) / 1000), start_timestamp_,
        #       'e:', datetime.fromtimestamp(int(end_timestamp_) / 1000), end_timestamp_)

        interval = '1m'

        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_timestamp_,
            "endTime": end_timestamp_
        }

        response = requests.get(url, params=params)
        full_interval_data = response.json()
        # print(f"---{full_interval_data}---\n\n\n")
        for data_to_min in full_interval_data:
            prices_dict = {
                'open_price': float(data_to_min[1]),
                'high_price': float(data_to_min[2]),
                'low_price': float(data_to_min[3]),
                'close_price': float(data_to_min[4]),
            }
            cur_time_prices = datetime.fromtimestamp(int(data_to_min[0]) / 1000)
            current_dict_[cur_time_prices] = prices_dict
            prices_in_interval_dict[cur_time_prices] = prices_dict

        return current_dict_

    different_times_hours_and_minutes = (end_time - start_time).total_seconds() / 3600

    new_start = start_time
    new_start_timestamp = int(new_start.timestamp() * 1000)
    new_end = new_start + timedelta(hours=8)
    new_end_timestamp = int(new_end.timestamp() * 1000)

    check_minimum = False

    current_dict = {}
    while different_times_hours_and_minutes > 8:
        different_times_hours_and_minutes -= 8

        current_dict = get_prices(new_start_timestamp, new_end_timestamp, current_dict)

        current_different_hours = int((start_time - new_start).total_seconds() / 3600)

        if wait_hours:
            if current_different_hours >= 24:
                check_minimum = True
        result = check_changing_in_prices_dictionary_interval(mode, symbol, open_price,
                                                              new_start, current_dict, check_minimum)
        if result in [1, -1]:
            return result

        new_start = new_end
        new_start_timestamp = int(new_start.timestamp() * 1000)
        new_end = new_start + timedelta(hours=8)
        new_end_timestamp = int(new_end.timestamp() * 1000)

    else:
        new_end = end_time
        new_end_timestamp = int(new_end.timestamp() * 1000)
        get_prices(new_start_timestamp, new_end_timestamp, current_dict)

        result = check_changing_in_prices_dictionary_interval(mode, symbol, open_price,
                                                              new_start, current_dict, check_minimum)

    return 0


def get_res_for_kline_bybit(symbol: str,
                            start: datetime,
                            end: datetime,
                            open_price: float,
                            mode: str,
                            wait_hours: bool
                            ) -> int:
    prices_in_interval_dict = {}
    print(f"Symbol: {symbol}")

    def get_prices(start_timestamp_, end_timestamp_, current_dict_: dict):
        # print('s:', datetime.fromtimestamp(int(start_timestamp_) / 1000), start_timestamp_,
        #       'e:', datetime.fromtimestamp(int(end_timestamp_) / 1000), end_timestamp_)

        interval = '1'
        category = "spot"

        url = f"{API_URL_BYBIT}/v5/market/kline"
        params = {
            "symbol": symbol,
            "interval": interval,
            "category": category,
            "start": start_timestamp_,
            "end": end_timestamp_
        }
        response = requests.get(url, params=params)
        full_data_json = response.json()
        result_data = full_data_json["result"]
        full_interval_data = result_data["list"][::-1]
        for data_to_min in full_interval_data:
            prices_dict = {
                'open_price': float(data_to_min[1]),
                'high_price': float(data_to_min[2]),
                'low_price': float(data_to_min[3]),
                'close_price': float(data_to_min[4]),
            }
            cur_time_prices = datetime.fromtimestamp(int(data_to_min[0]) / 1000)
            current_dict_[cur_time_prices] = prices_dict
            prices_in_interval_dict[cur_time_prices] = prices_dict

        return current_dict_

    different_times_hours_and_minutes = (end - start).total_seconds() / 3600

    new_start = start
    new_start_timestamp = int(new_start.timestamp() * 1000)
    new_end = new_start + timedelta(hours=3)
    new_end_timestamp = int(new_end.timestamp() * 1000)

    check_minimum = False

    current_dict = {}
    while different_times_hours_and_minutes > 3:
        different_times_hours_and_minutes -= 3

        current_dict = get_prices(new_start_timestamp, new_end_timestamp, current_dict)

        current_different_hours = int((start - new_start).total_seconds() / 3600)

        if wait_hours:
            if current_different_hours >= 24:
                check_minimum = True
        result = check_changing_in_prices_dictionary_interval(mode, symbol, open_price,
                                                              new_start, current_dict, check_minimum)
        if result in [1, -1]:
            return result

        new_start = new_end
        new_start_timestamp = int(new_start.timestamp() * 1000)
        new_end = new_start + timedelta(hours=3)
        new_end_timestamp = int(new_end.timestamp() * 1000)

    else:
        new_end = end
        new_end_timestamp = int(new_end.timestamp() * 1000)
        current_dict = get_prices(new_start_timestamp, new_end_timestamp, current_dict)

        result = check_changing_in_prices_dictionary_interval(mode, symbol, open_price,
                                                              new_start, current_dict, check_minimum)

        if result in [1, -1]:
            return result


    return 0


def check_changing_in_interval(mode: str,
                               symbol: str,
                               open_price: float,
                               open_time: datetime,
                               close_time: datetime,
                               platform_name: str,
                               wait_hours: bool = False):
    if platform_name == "BYBIT":
        result = get_res_for_kline_bybit(symbol, open_time, close_time, open_price, mode, wait_hours)
    elif platform_name == "BINANCE":
        result = get_res_for_kline_binance(symbol, open_time, close_time, open_price, mode, wait_hours)
    return result


def check_changing_in_prices_dictionary_interval(mode: str,
                                                 symbol: str,
                                                 open_price: float,
                                                 open_time: datetime,
                                                 prices_dictionary: dict,
                                                 check_minimum: bool
                                                 ) -> int:
    one_percent = open_price / 100
    if mode == 'long':
        long_price_prof = open_price + one_percent * 5
        close_price = open_price - one_percent * 3
        # print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: "
        #       f"{one_percent}\nlong_price_prof: {long_price_prof}") # \nclose_price: {close_price}
        for time_, prices in prices_dictionary.items():
            max_price_minute = prices['high_price']
            min_price_minute = prices['low_price']
            if max_price_minute >= long_price_prof:  # в интервале лонг прогнозирован правильно
                print('TIME-WIN:', time_, max_price_minute)
                # print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: "
                #       f"{one_percent}\nlong_price_prof: {long_price_prof}")
                return 1
            elif check_minimum and min_price_minute <= close_price:  # в интервале лонг прогнозирован неправильно
                print('TIME-LOS:', time_, min_price_minute)
                return -1

    elif mode == 'short':
        short_price_prof = open_price - one_percent * 5
        close_price = open_price + one_percent * 3
        # print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: "
        #       f"{one_percent}\nshort_price_prof: {short_price_prof}") # \nclose_price: {close_price}

        for time_, prices in prices_dictionary.items():
            max_price_minute = prices['high_price']
            min_price_minute = prices['low_price']
            if min_price_minute <= short_price_prof:  # в интервале шорт прогнозирован правильно
                print('time win:', time_, max_price_minute)
                print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: "
                      f"{one_percent}\nlong_price_prof: {short_price_prof}")
                return 1
            elif max_price_minute >= close_price:  # в интервале шорт прогнозирован неправильно
                print('time los:', time_, min_price_minute)
                return -1
    return 0


def get_count_to_print(n: int) -> int:
    if not n:
        return 0
    formula_Stregera = int(1 + 3.3222 * log10(n))
    return formula_Stregera


def get_data_in_range(start: int, end: int) -> dict:
    count = start
    ret_dict = {}
    df = DATA_DF[start:end]
    print(df.head(5), df.tail(5))
    for row in df.itertuples(index=False):
        count += 1
        mode = row.MODE
        confirmation = row.CONFIRMATION
        if count - 1 < start or count - 1 > end or mode == "MODE" or confirmation in ["1", "-1"]: #
            continue
        ret_dict[count] = row
    return ret_dict


def check_data_forecasts():
    """
    для добавления из FILE_DATA_PATH в FILE_DATA_PATH_WITH_SOME_CONFIRMATION:
from config import FILE_DATA_PATH,FILE_DATA_PATH_WITH_SOME_CONFIRMATION
import pandas as pd

OLD_DF = pd.read_csv(FILE_DATA_PATH, index_col=False)
DATA_DF = pd.read_csv(FILE_DATA_PATH_WITH_SOME_CONFIRMATION, index_col=0)
df_tmp = pd.concat([DATA_DF, OLD_DF[1391:]], ignore_index=True)

    (del df_tmp['Unnamed: 0'])

    df_tmp.to_csv(FILE_DATA_PATH_WITH_SOME_CONFIRMATION)
    :return:
    """
    total_forecasts_dict = {"win": 0,
                            "los": 0}
    count, use_count = 0, False
    list_win, list_los, list_no_res = [], [], []
    dict_allowed_rows = get_data_in_range(RANGE_TO_GET_ROWS[0], RANGE_TO_GET_ROWS[1])


    for index, row in dict_allowed_rows.items():
        if count == 10 and use_count:
            break
        mode = row.MODE
        if mode == 'short':
            continue
        print(index - 1)
        symbol = row.SYMBOL
        time_open = row[4]
        price_open = float(row[5])
        platform_name = row[6]
        if platform_name == 'BINANCE':
            continue
        time_open_datetime = datetime.strptime(time_open, '%Y-%m-%d %H:%M:%S')

        time_now = datetime.now().replace(second=0, microsecond=0)
        print(time_open_datetime, time_now)
        res = check_changing_in_interval(mode, symbol, price_open, time_open_datetime,
                                         time_now, platform_name, WAIT_HOURS)
        if res == 1:
            total_forecasts_dict["win"] += 1
            list_win.append(symbol)

        elif res == -1:
            total_forecasts_dict["los"] += 1
            list_los.append(symbol)
        else:
            list_no_res.append(symbol)
        DATA_DF.loc[index - 1, "CONFIRMATION"] = res
        count += 1

    DATA_DF.to_csv(FILE_DATA_PATH_WITH_SOME_CONFIRMATION)

    set_win, set_los, set_no_res = set(list_win), set(list_los), set(list_no_res)

    total_sum = total_forecasts_dict["win"] - total_forecasts_dict["los"]
    percent_profit = 0.02 * total_forecasts_dict["win"] - 0.1 * total_forecasts_dict["los"] # 0.03 * total_forecasts_dict["los"]
    try:
        percent_success_deals = (total_forecasts_dict["win"] /
                                 (total_forecasts_dict["win"] + total_forecasts_dict["los"] + len(list_no_res))) * 100
    except ZeroDivisionError:
        percent_success_deals = 0
    # try:
    #     percent_success_deals_set = (len(set_win) / (len(set_win) + len(set_los))) * 100
    # except ZeroDivisionError:
    #     percent_success_deals_set = 0
    # percent_profit_to_set = 0.02 * len(set_win) - 0.03 * len(set_los)

    sum_of_one_deal = 5

    print(f"\n"
          f"Forecasts count: {len(DATA_DF)} (cur on count {count})\n"
          f"Correctness of forecasts: {total_forecasts_dict}\n" # , (set: 'win': {len(set_win)}, 'los' {len(set_los)})
          f"Percent of success deals: {int(percent_success_deals)}%\n" # , (set: {int(percent_success_deals_set)}%)
          f"Total sum: {total_sum}\n\n"
          f"Percent profit: {percent_profit}%. "
          f"If sum to one deal = ${sum_of_one_deal}, profit: ${sum_of_one_deal * percent_profit}\n"
          # f"Percent profit to set: {percent_profit_to_set}%. "
          f"If sum to one deal = ${sum_of_one_deal}\n\n" # , profit to set: ${sum_of_one_deal*percent_profit_to_set}
          f"list with win symbols: {list_win[:get_count_to_print(len(list_win)):]} (len: {len(list_win)})\n"
          # f"len SET with win symbols: {len(set_win)}\n"
          f"list with los symbols: {list_los[:get_count_to_print(len(list_los)):]} (len: {len(list_los)})\n"
          # f"len SET with los symbols: {len(set_los)}\n"
          f"list with symbols without result: {list_no_res[:get_count_to_print(len(list_no_res)):]} "
          f"len: ({len(list_no_res)})\n"
          # f"len SET without result symbols: {len(set_no_res)}"
          )


check_data_forecasts()






