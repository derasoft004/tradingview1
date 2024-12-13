import argparse
from datetime import timedelta
import threading

from tradingview_ta import Interval

from config import FILE_SYMBOLS_PATH, FILE_DATA_PATH
from trvw_funcs import get_list_symbols, data_collection


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-int', '--interval',
                       type=str,
                       help='Interval that will using to make currency forecasts\n\n'
                            ''
                            'Allowed intervals:\n'
                            ' am (a minute)\n'
                            ' fm (fifteen minutes)\n'
                            ' ah (a hour)\n'
                            ' fh (four hours)\n'
                            ' ad (a day)'
                       )
    parser.add_argument('-utf', '--use_two_forecasts',
                       type=str,
                       help='Flag to use the same minute and hour forecasts\n\n'
                            ''
                            'Allowed flags:\n'
                            ' True\n'
                            ' False'
                       )
    parser.add_argument('-uol', '--only_long',
                       type=str,
                       help='Flag to use only long forecasts\n\n'
                            ''
                            'Allowed flags:\n'
                            ' True\n'
                            ' False'
                       )

    args = parser.parse_args()

    match args.interval:
        case 'am':
            INTERVAL = Interval.INTERVAL_1_MINUTE
            INTERVAL_TYPE = 'a minute'
            TIME_SECONDS = 60
            INTERVAL_CLEAR_TIMER = timedelta(minutes=1)
        case 'fm':
            INTERVAL = Interval.INTERVAL_15_MINUTES
            INTERVAL_TYPE = 'fifteen minutes'
            TIME_SECONDS = 900
            INTERVAL_CLEAR_TIMER = timedelta(minutes=7)
        case 'ah':
            INTERVAL = Interval.INTERVAL_1_HOUR
            INTERVAL_TYPE = 'a hour'
            TIME_SECONDS = 3600
            INTERVAL_CLEAR_TIMER = timedelta(minutes=30)
        case 'fh':
            INTERVAL = Interval.INTERVAL_4_HOURS
            INTERVAL_TYPE = 'four hours'
            TIME_SECONDS = 3600 * 4
            INTERVAL_CLEAR_TIMER = timedelta(hours=1)
        case 'ad':
            INTERVAL = Interval.INTERVAL_1_DAY
            INTERVAL_TYPE = 'a day'
            TIME_SECONDS = 3600 * 24
            INTERVAL_CLEAR_TIMER = timedelta(hours=6)

    match args.use_two_forecasts:
        case 'y':
            USE_TWO_FORECASTS = True
        case 'n':
            USE_TWO_FORECASTS = False

    match args.only_long:
        case 'y':
            ONLY_LONG = True
        case 'n':
            ONLY_LONG = False

    symbol_list = get_list_symbols(FILE_SYMBOLS_PATH)
    print(f"symbol_list len: {len(symbol_list)}")
    data_collection(symbol_list, INTERVAL, INTERVAL_TYPE, FILE_DATA_PATH, TIME_SECONDS,
                    INTERVAL_CLEAR_TIMER, ONLY_LONG, USE_TWO_FORECASTS)


if __name__ == '__main__':
    main()
