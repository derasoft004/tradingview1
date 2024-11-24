import csv
import os
from datetime import datetime, timedelta, timezone
import logging
import time
from os import close

import requests
import pytz

from tradingview_ta import TA_Handler, Interval, Exchange
from binance.um_futures import UMFutures

from config import FILE_DATA_PATH


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
    activiti['SYMBOL'] = symbol
    return activiti


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
        logging.error(not_found_error)
        return


def make_offer_link():
    """
    link binance api: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/public-api-endpoints#new-order-trade
    form: POST /api/v3/order
    :return:
    """
    pass


def data_collection(symbols_list: list,
                    interval: Interval,
                    interval_type: str,
                    file_data_store: str,
                    time_seconds: int,
                    interval_clear_timer: timedelta) -> None:
    """
    функция собирает прогнозы по всем монетам в выбранном интервале,
     собирает данные в определенном формате (см список 'fields_names')

    :param symbols_list:
    :param interval:
    :param interval_type:
    :param file_data_store:
    :param time_seconds:
    :param interval_clear_timer:
    :return:
    """
    fields_names = ['MODE', 'INTERVAL', 'SYMBOL', 'FORECAST', 'TIME-OPEN', 'PRICE-OPEN',
                    'TIME-MAX-PRICE', 'MAX-PRICE', 'TIME-TO-MAX-PRICE',
                    'TIME-MIN-PRICE', 'MIN-PRICE', 'TIME-TO-MIN-PRICE',
                    'CONFIRMATION']

    write_data_to_csv_file(FILE_DATA_PATH, fields_names)

    longs, shorts = [], []

    forecasts_dict = {symbol_name: {} for symbol_name in symbols_list}
    round_number = 0
    time_start = datetime.now().replace(second=0) # время по дубай
    next_time = time_start + interval_clear_timer
    print('now time is: ', time_start, 'next time is: ', next_time.strftime('%Y-%m-%d %H:%M:%S'))
    while True:
        print(f"==========NEW={round_number}=ROUND==========\n"
              f"longs: {longs}\n"
              f"shorts: {shorts}")
        for symbol in symbols_list:
            time_now = datetime.now().replace(second=0) # время по дубай
            try:
                forecast = get_symbol_forecast(symbol, interval)
                forecast_string = ';'.join([f"{key}:{value}" for key, value in forecast.items()])
                fields_symbol_data = ['', interval_type, symbol, forecast_string, time_now, None,
                                      None, None, None,
                                      None, None, None,
                                      None]
                if symbol in longs or symbol in shorts:
                    # проверим, не обновился прогноз ли для символа
                    if forecast != forecasts_dict[symbol]:
                        forecasts_dict[symbol] = forecast
                            # todo удаление из лонгов/шортов происходит только если сделка завершена
                            #  + результат сделки нужно сохранять; сделать проверку в цикле (интервально во времени)
                            # if symbol in longs:
                            #     print(f"DELETE {symbol} from longs")
                            #     longs.remove(symbol)
                            # elif symbol in shorts:
                            #     print(f"DELETE {symbol} from shorts")
                            #     shorts.remove(symbol)
                    else:
                        continue

                if int(forecast['NEUTRAL']) <= 10:
                    match forecast['RECOMMENDATION']:
                        case 'STRONG_BUY':
                            fields_symbol_data[0] = 'long'
                            longs.append(symbol)
                            write_data_to_csv_file(file_data_store, fields_symbol_data)
                            print(f"FORECAST FOR {symbol}: {forecast}")
                            forecasts_dict[symbol] = forecast
                        case 'STRONG_SELL':
                            fields_symbol_data[0] = 'short'
                            shorts.append(symbol)
                            write_data_to_csv_file(file_data_store, fields_symbol_data)
                            print(f"FORECAST FOR {symbol}: {forecast}")
                            forecasts_dict[symbol] = forecast


                time.sleep(0.01)
            except IndentationError as e:
                logging.error(f"unexpected indent (?); {e}")

            except Exception as e:
                logging.error(f"func 'data_collection' cycle error, symbol: {symbol}; {e}")
                symbols_list.remove(symbol)

        round_number += 1

        if time_now >= next_time:
            next_time = time_now + interval_clear_timer
            print('now time is: ', time_now, 'next time is: ', next_time.strftime('%Y-%m-%d %H:%M:%S'))
            longs.clear()
            shorts.clear()

        # time.sleep(time_seconds)

