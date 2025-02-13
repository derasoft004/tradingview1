import csv
import os
from datetime import datetime, timedelta
import logging
import time
from typing import Tuple
import requests
import telebot
import time

from tradingview_ta import TA_Handler, Interval
from pybit.unified_trading import HTTP

from bot_handler import send_message, get_last_message
from config import (FILE_DATA_PATH, FILE_SYMBOLS_PATH, API_URL_BYBIT, ONE_DEAL_BET,
                    API_KEY_BYBIT, API_SECRET_BYBIT, TELEGRAM_TOKEN, CHAT_ID, TRVW_LINK_SYMBOL)


# bot = telebot.TeleBot(TELEGRAM_TOKEN)
#
#
# def wait_for_response_(chat_id):
#     @bot.message_handler(func=lambda message: True)
#     def handle_response(message):
#         if message.chat.id == chat_id:
#             print(message.text)
#             time.sleep(3)
#             if message.text:
#                 bot.reply_to(message, "Спасибо за ваш ответ!")
#             else:
#                 handle_response(message)
#             print('ответ обработан')
#
#
# def run_bot():
#     bot.polling(none_stop=True)


def get_symbol_forecast(symbol: str, interval: Interval) -> dict:
    """
    функция собирает словарь с элементами прогноза и добавляет имя монеты с ключом 'SYMBOL'

    keys:
        RECOMMENDATION
        BUY
        SELL
        NEUTRAL
        SYMBOL
    example:
        {'RECOMMENDATION': 'NEUTRAL', 'BUY': 8, 'SELL': 8, 'NEUTRAL': 10, 'SYMBOL': '1INCHUSDT'}

    :param symbol:
    :param interval:
    :return:
    """
    output = TA_Handler(
        symbol=symbol,
        screener='Crypto',
        exchange='Binance',
        interval=interval
    )
    activiti = output.get_analysis().summary
    # activiti['SYMBOL'] = symbol
    return activiti


def get_symbol_joint_forecast(symbol: str) -> dict:
    output_m = TA_Handler(
        symbol=symbol,
        screener='Crypto',
        exchange='Binance',
        interval=Interval.INTERVAL_1_MINUTE
    )
    output_h = TA_Handler(
        symbol=symbol,
        screener='Crypto',
        exchange='Binance',
        interval=Interval.INTERVAL_1_HOUR
    )
    if output_h.get_analysis().summary["RECOMMENDATION"] == output_m.get_analysis().summary["RECOMMENDATION"]:
        return output_h.get_analysis().summary
    return {'RECOMMENDATION': 'NEUTRAL', 'BUY': 0, 'SELL': 0, 'NEUTRAL': 0}


def get_list_symbols(file_path: str) -> list:
    """
    функиця достает список из 374 монет и возвращает их список

    в случае ошибки возвращает пустой список

    :param file_path:
    :return:
    """
    try:
        with open(file_path, 'r') as file:
            return file.read().split(',')
    except FileNotFoundError as not_found_error:
        logging.error(not_found_error)
    return []


def write_data_to_csv_file(file_path: str, fields_data_list: list) -> None:
    """
    используется для записи наименований полей если файла не существует и дополнения данными в противном случае

    :param file_path:
    :param fields_data_list: названия полей или параметры
    :return:
    """
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as csv_file:
                writer_head = csv.DictWriter(csv_file, fieldnames=fields_data_list)
                writer_head.writeheader()
                logging.info(f'file {file_path} is created.\n')
        else:
            with open(file_path, 'a') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(fields_data_list)
                logging.info(f'\'fields_data_list\' was writen to file {file_path} successfully.\n')
    except FileNotFoundError as not_found_error:
        print(not_found_error)
        return


def get_kline_bybit_open_price(symbol: str, interval: str, category: str, start) -> float:
    url = f"{API_URL_BYBIT}/v5/market/kline"

    start_modify = int(start.timestamp() * 1000)

    params = {
        "symbol": symbol,
        "interval": interval,
        "category": category,
        "start": start_modify,
        "end": start_modify
    }
    response = requests.get(url, params=params)
    full_data_json = response.json()
    # print(full_data_json)
    result = full_data_json["result"]
    if not len(result):
        raise AttributeError
    full_minute_data = result["list"][0]
    open_price = full_minute_data[1]

    return open_price


def get_kline_binance_open_price(symbol: str, interval: str, open_time: datetime) -> float:
    open_normal_time = int(open_time.timestamp() * 1000)
    url = f'https://api.binance.com/api/v3/klines'

    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": open_normal_time,
        "endTime": open_normal_time
    }

    response = requests.get(url, params=params)
    full_data_json = response.json()
    open_price = float(full_data_json[0][1])

    return open_price


def get_base_precision_count_nums(base_precision: str) -> int:
    return len(base_precision.split('.')[1])


def round_down(value: float, decimal_places):
    value_str = str(value)
    integer_part, decimal_part = value_str.split('.')

    if decimal_places == 0:
        return float(integer_part)  # Возвращаем только целую часть

    if len(decimal_part) > decimal_places:
        rounded_decimal = decimal_part[:decimal_places]
        return float(f"{integer_part}.{rounded_decimal}")
    else:
        rounded_decimal = decimal_part.ljust(decimal_places, '0')
        return float(f"{integer_part}.{rounded_decimal}")


def get_open_price(symbol: str, target_time) -> Tuple:
    interval = "1"
    category = "spot"

    platform_name = "BYBIT"
    try:
        price_open = get_kline_bybit_open_price(symbol, interval, category, target_time)
    except AttributeError:
        platform_name = "BINANCE"
        interval = "1m"
        price_open = get_kline_binance_open_price(symbol, interval, target_time)

    return platform_name, price_open


def data_collection(symbols_list: list,
                    interval: Interval,
                    interval_type: str,
                    file_data_store: str,
                    time_seconds: int,
                    interval_clear_timer: timedelta,
                    only_long: bool,
                    use_two_forecasts: bool, ) -> None:
    """
    функция собирает прогнозы по всем монетам в выбранном интервале,
     собирает данные в определенном формате (см список 'fields_names')

    :param symbols_list:
    :param interval:
    :param interval_type:
    :param file_data_store:
    :param time_seconds:
    :param interval_clear_timer:
    :param only_long:
    :param use_two_forecasts:
    :return:
    """
    fields_names = ['MODE', 'INTERVAL', 'SYMBOL', 'FORECAST', 'TIME-OPEN', 'PRICE-OPEN', 'PLATFORM_NAME',
                    'CONFIRMATION', ]

    write_data_to_csv_file(FILE_DATA_PATH, fields_names)

    longs, shorts = set(), set()

    # forecasts_dict = {symbol_name: {} for symbol_name in symbols_list}
    round_number = 0
    time_start = datetime.now().replace(second=0, microsecond=0)  # время по дубай
    next_time = time_start + interval_clear_timer
    print(f"now time is: {time_start} next time is: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")

    client = HTTP(
        api_key=API_KEY_BYBIT,
        api_secret=API_SECRET_BYBIT
    )

    # на тестах
    availableWithdrawal = client.get_wallet_balance(
        accountType='UNIFIED',
        coin='USDT'
    )
    totalMarginBalance = float(availableWithdrawal["result"]["list"][0]["totalMarginBalance"])

    while True:
        print(f"==========NEW={round_number}=ROUND==========\n"
              f"longs: {longs}\n"
              f"shorts: {shorts}")
        print(f"==========NEW={round_number}=ROUND==========\n")
        symbols_list_except = []

        for symbol in symbols_list:
            if symbol in ["BTCUSDT", "BTCUSDC", "ETHUSDT", "ETHUSDC"]:
                continue
            time_now = datetime.now().replace(second=0, microsecond=0)  # время по дубай
            try:
                if use_two_forecasts:
                    forecast = get_symbol_joint_forecast(symbol)
                else:
                    forecast = get_symbol_forecast(symbol, interval)
                    # sent_message = send_message(symbol + forecast['RECOMMENDATION'])
                    # print(f'отправлено сообщение по {symbol}')
                    # new_message = get_last_message(sent_message)
                    # print(new_message)

                forecast_string = ';'.join([f"{value}" for key, value in forecast.items()])
                fields_symbol_data = ['', interval_type, symbol, forecast_string, time_now, None, None, None]
                if symbol in longs or symbol in shorts:
                    continue

                if int(forecast['NEUTRAL']) <= 10:
                    try:
                        session_result = client.get_instruments_info(
                            category="spot",
                            symbol=symbol,
                        )['result']
                        lotSizeFilter = session_result['list'][0]['lotSizeFilter']
                        # print(session_result)
                        minOrderQty = float(lotSizeFilter['minOrderQty'])
                        minOrderAmt = float(lotSizeFilter['minOrderAmt'])

                    except IndexError:
                        # print(f"{symbol} is symbol from BINANCE ({e})")
                        minOrderQty, minOrderAmt = 0, 0

                    match forecast['RECOMMENDATION']:
                        case 'STRONG_BUY':
                            platform_name, price = get_open_price(symbol, time_now)
                            if platform_name == "BINANCE":
                                continue
                            min_order_cost = minOrderQty * float(price)
                            fields_symbol_data[0] = 'long'
                            fields_symbol_data[5] = price
                            fields_symbol_data[6] = platform_name
                            write_data_to_csv_file(file_data_store, fields_symbol_data)

                            # нужно когда каждый раз именно баланс берем (в реальной работе)
                            # availableWithdrawal = client.get_wallet_balance(
                            #     accountType='UNIFIED',
                            #     coin='USDT'
                            # )
                            # totalMarginBalance = float(availableWithdrawal["result"]["list"][0]["totalMarginBalance"])

                            print(f"{fields_symbol_data}, записано; min cost:, ${min_order_cost}, (${minOrderAmt})")
                            if min_order_cost < ONE_DEAL_BET and minOrderAmt < ONE_DEAL_BET:
                                if totalMarginBalance > 1:
                                    # precision_count_nums = get_base_precision_count_nums(lotSizeFilter["basePrecision"])
                                    # correct_qty = round_down(minOrderQty * (1 + COMMISSION_RATE), precision_count_nums)
                                    # correct_qty = int(minOrderQty) + 1
                                    current_order_cost = minOrderQty * float(price)
                                    # print(session_result)

                                    result_about_symbol = \
                                        (f'"{symbol}"\n'
                                         f'{TRVW_LINK_SYMBOL}{symbol}\n'
                                         f'можно купить {minOrderQty} этой монеты на ${current_order_cost} \n'
                                         f'баланс маржи сейчас: ${totalMarginBalance}, ' 
                                         f'баланс маржи после покупки: ${totalMarginBalance - current_order_cost}')

                                    sent_message = send_message(result_about_symbol)
                                    print(f'отправлено сообщение по {symbol} (маржа {totalMarginBalance})')
                                    # print(result_about_symbol)
                                    new_message = get_last_message(sent_message)
                                    print(new_message)

                                    if new_message == 'да':
                                        totalMarginBalance -= current_order_cost
                                        print('маржа да', totalMarginBalance)
                                    elif new_message == 'нет':
                                        print('маржа нет', totalMarginBalance)
                                        continue

                                elif totalMarginBalance <= 1:
                                    print('баланс слишком мал!')

                            longs.add(symbol)

                        case 'STRONG_SELL':
                            if only_long:
                                # print(f"FORECAST FOR {symbol}: {forecast} - не записано")
                                continue
                            platform_name, price = get_open_price(symbol, time_now)
                            if platform_name == "BINANCE":
                                continue
                            min_order_cost = minOrderQty * float(price)
                            fields_symbol_data[0] = 'short'
                            fields_symbol_data[5] = price
                            fields_symbol_data[6] = platform_name
                            write_data_to_csv_file(file_data_store, fields_symbol_data)
                            print(f"{fields_symbol_data}, записано; min cost:, ${min_order_cost}, (${minOrderAmt})")
                            shorts.add(symbol)
                            # print(f"FORECAST FOR {symbol}: {forecast} ЗАПИСАНО")
                            # forecasts_dict[symbol] = forecast

                time.sleep(0.01)

            except IndentationError as e:
                print(f"unexpected indent (?); {e}")

            except Exception as e:
                print(f"func 'data_collection' cycle error, symbol: {symbol}; {e}")
                symbols_list.remove(symbol)
                symbols_list_except.append(symbol)

        round_number += 1

        with open(FILE_SYMBOLS_PATH, 'w') as smbls_file:
            smbls_file.write(','.join([x for x in symbols_list if x not in symbols_list_except]))

        if time_now >= next_time:
            next_time = time_now + interval_clear_timer
            print(f"now time is: {time_now} next time is: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
            longs.clear()
            shorts.clear()

        # time.sleep(time_seconds)
