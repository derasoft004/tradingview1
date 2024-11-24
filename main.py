import argparse
from datetime import timedelta

from tradingview_ta import Interval

from config import FILE_SYMBOLS_PATH, FILE_DATA_PATH
from trvw_funcs import get_list_symbols, data_collection


def main():

    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-int', '--interval',
                       type=str,
                       help='Interval that will using to make currency forecasts\n\n'
                            ''
                            'Allowed intervals:\n'
                            ' am (a minute)\n'
                            ' fm (fifteen minutes)\n'
                            ' ah (a hour)\n'
                            ' fh (four hours)\n'
                            ' ad (a day)')

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
            INTERVAL_CLEAR_TIMER = timedelta(minutes=15)
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

    symbol_list = get_list_symbols(FILE_SYMBOLS_PATH)

    data_collection(symbol_list, INTERVAL, INTERVAL_TYPE, FILE_DATA_PATH, TIME_SECONDS, INTERVAL_CLEAR_TIMER)


if __name__ == '__main__':
    main()
