from math import log10

import pandas as pd
from datetime import datetime, timedelta
import requests
from config import API_URL_BYBIT, FILE_DATA_PATH_WITH_SOME_CONFIRMATION

DATA_DF = pd.read_csv(FILE_DATA_PATH_WITH_SOME_CONFIRMATION)


def get_kline_binance(symbol: str, start_time: datetime, end_time: datetime) -> dict:
    prices_in_interval_dict = {}

    url = f'https://api.binance.com/api/v3/klines'

    def get_prices(start_timestamp_, end_timestamp_):
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
            prices_in_interval_dict[cur_time_prices] = prices_dict

    different_times_hours_and_minutes = (end_time - start_time).total_seconds() / 3600

    new_start = start_time
    new_start_timestamp = int(new_start.timestamp() * 1000)
    new_end = new_start + timedelta(hours=8)
    new_end_timestamp = int(new_end.timestamp() * 1000)

    while different_times_hours_and_minutes > 8:
        different_times_hours_and_minutes -= 8

        get_prices(new_start_timestamp, new_end_timestamp)

        new_start = new_end
        new_start_timestamp = int(new_start.timestamp() * 1000)
        new_end = new_start + timedelta(hours=8)
        new_end_timestamp = int(new_end.timestamp() * 1000)

    else:
        new_end = end_time
        new_end_timestamp = int(new_end.timestamp() * 1000)
        get_prices(new_start_timestamp, new_end_timestamp)

    return prices_in_interval_dict


def get_kline_bybit(symbol: str, start: datetime, end: datetime) -> dict:
    prices_in_interval_dict = {}

    def get_prices(start_timestamp_, end_timestamp_):
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
        result = full_data_json["result"]
        full_interval_data = result["list"][::-1]
        # print(f"---{full_interval_data}---\n\n\n")
        for data_to_min in full_interval_data:
            prices_dict = {
                'open_price': float(data_to_min[1]),
                'high_price': float(data_to_min[2]),
                'low_price': float(data_to_min[3]),
                'close_price': float(data_to_min[4]),
            }
            cur_time_prices = datetime.fromtimestamp(int(data_to_min[0]) / 1000)
            prices_in_interval_dict[cur_time_prices] = prices_dict

    different_times_hours_and_minutes = (end - start).total_seconds() / 3600

    new_start = start
    new_start_timestamp = int(new_start.timestamp() * 1000)
    new_end = new_start + timedelta(hours=3)
    new_end_timestamp = int(new_end.timestamp() * 1000)

    while different_times_hours_and_minutes > 3:
        different_times_hours_and_minutes -= 3

        get_prices(new_start_timestamp, new_end_timestamp)

        new_start = new_end
        new_start_timestamp = int(new_start.timestamp() * 1000)
        new_end = new_start + timedelta(hours=3)
        new_end_timestamp = int(new_end.timestamp() * 1000)

    else:
        new_end = end
        new_end_timestamp = int(new_end.timestamp() * 1000)
        get_prices(new_start_timestamp, new_end_timestamp)


    return prices_in_interval_dict



def check_changing_in_interval(mode: str,
                               symbol: str,
                               open_price: float,
                               open_time: datetime,
                               close_time: datetime,
                               platform_name: str,
                               show_lst_no_res: bool = False):
    if platform_name == "BYBIT":
        prices_dictionary = get_kline_bybit(symbol, open_time, close_time)
    elif platform_name == "BINANCE":
        prices_dictionary = get_kline_binance(symbol, open_time, close_time)
    one_percent = open_price / 100
    print(f"Symbol: {symbol}")
    if mode == 'long':
        long_price_prof = open_price + one_percent * 5
        close_price = open_price - one_percent * 3
        print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: "
              f"{one_percent}\nlong_price_prof: {long_price_prof}\nclose_price: {close_price}")
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
        print(f"open_time: {open_time}\nopen_price: {open_price}\n1%: "
              f"{one_percent}\nshort_price_prof: {short_price_prof}\nclose_price: {close_price}")

        for time_, prices in prices_dictionary.items():
            max_price_minute = prices['high_price']
            min_price_minute = prices['low_price']
            if min_price_minute <= short_price_prof: # в интервале шорт прогнозирован правильно
                print('time win:', time_, max_price_minute)
                return 1
            elif max_price_minute >= close_price: # в интервале шорт прогнозирован неправильно
                print('time los:', time_, min_price_minute)
                return -1
    if show_lst_no_res:
        print(prices_dictionary.items())
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
        if count - 1 < start or count - 1 > end or mode == "MODE":
            continue
        ret_dict[count] = row
    return ret_dict


def check_data_forecasts():
    """
    для добавления из FILE_DATA_PATH в FILE_DATA_PATH_WITH_SOME_CONFIRMATION:
    from config import FILE_DATA_PATH,FILE_DATA_PATH_WITH_SOME_CONFIRMATION, FILE_DATA_PATH_TMP, FILE_DATA_PATH_WITH_SOME_CONFIRMATION_TMP
    import pandas as pd

    OLD_DF = pd.read_csv(FILE_DATA_PATH)
    DATA_DF = pd.read_csv(FILE_DATA_PATH_WITH_SOME_CONFIRMATION, index_col=0)
    df_tmp = pd.concat([DATA_DF, OLD_DF[1391:]], ignore_index=True)
    :return:
    """
    total_forecasts_dict = {"win": 0,
                            "los": 0}
    count, use_count = 0, False
    list_win, list_los, list_no_res = [], [], []
    show_lst_no_res = False
    dict_allowed_rows = get_data_in_range(1391, 1983) # (107, 470)

    for index, row in dict_allowed_rows.items():
        print(index - 1)
        if count == 10 and use_count:
            break
        mode = row.MODE
        symbol = row.SYMBOL
        time_open = row[5]
        price_open = float(row[6])
        platform_name = row[7]
        time_open_datetime = datetime.strptime(time_open, '%Y-%m-%d %H:%M:%S')

        time_now = datetime.now().replace(second=0, microsecond=0)
        print(time_open_datetime, time_now)
        res = check_changing_in_interval(mode, symbol, price_open, time_open_datetime, time_now, platform_name, show_lst_no_res)
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

    DATA_DF.to_csv(FILE_DATA_PATH_WITH_SOME_CONFIRMATION, index=False)

    set_win, set_los, set_no_res = set(list_win), set(list_los), set(list_no_res)

    total_sum = total_forecasts_dict["win"] - total_forecasts_dict["los"]
    percent_profit = 0.05 * total_forecasts_dict["win"] - 0.03 * total_forecasts_dict["los"]
    percent_success_deals = (total_forecasts_dict["win"] /
                             (total_forecasts_dict["win"] + total_forecasts_dict["los"])) * 100
    percent_success_deals_set = (len(set_win) / (len(set_win) + len(set_los))) * 100
    percent_profit_to_set = 0.05 * len(set_win) - 0.03 * len(set_los)

    sum_of_one_deal = 10

    print(f"\n"
          f"Forecasts count: {len(DATA_DF)} (cur on count {count})\n"
          f"Correctness of forecasts: {total_forecasts_dict}, (set: 'win': {len(set_win)}, 'los' {len(set_los)})\n"
          f"Percent of success deals: {int(percent_success_deals)}%, (set: {int(percent_success_deals_set)}%)\n"
          f"Total sum: {total_sum}\n\n"
          f"Percent profit: {percent_profit}%. "
          f"If sum to one deal = ${sum_of_one_deal}, profit: ${sum_of_one_deal*percent_profit}\n"
          f"Percent profit to set: {percent_profit_to_set}%. "
          f"If sum to one deal = ${sum_of_one_deal}, profit to set: ${sum_of_one_deal*percent_profit_to_set}\n\n"
          f"list with win symbols: {list_win[:get_count_to_print(len(list_win)):]} (len: {len(list_win)})\n"
          f"len SET with win symbols: {len(set_win)}\n"
          f"list with los symbols: {list_los[:get_count_to_print(len(list_los)):]} (len: {len(list_los)})\n"
          f"len SET with los symbols: {len(set_los)}\n"
          f"list with symbols without result: {list_no_res[:get_count_to_print(len(list_no_res)):]} "
          f"len: ({len(list_no_res)})\n"
          f"len SET without result symbols: {len(set_no_res)}"
          )


check_data_forecasts()






