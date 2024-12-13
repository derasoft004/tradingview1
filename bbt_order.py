from unicodedata import category

from pybit.unified_trading import HTTP
import json

from config import API_KEY_BYBIT, API_SECRET_BYBIT


client = HTTP(
    api_key=API_KEY_BYBIT,
    api_secret=API_SECRET_BYBIT
)


def round_down(value: float, nums: int) -> float:
    factor = 1 / (10 ** nums)
    return (value // factor) * factor


def view_response(response_) -> None:
    print(json.dumps(response_, indent=4))


def get_base_precision_count_nums(base_precision: str) -> int:
    return len(base_precision.split('.')[1])


# PORTALUSDT_info = client.get_instruments_info(
#                     category="spot",
#                     symbol="PORTALUSDT",
#                 )
# view_response(
#     PORTALUSDT_info
# )
# print(get_base_precision_count_nums(PORTALUSDT_info["result"]["list"][0]["lotSizeFilter"]["basePrecision"]))


availableWithdrawal = client.get_wallet_balance(
    accountType='UNIFIED',
    coin='USDT'
)
view_response(
    availableWithdrawal
)

print(availableWithdrawal["result"]["list"][0]["totalMarginBalance"])





# 1839198852113329920 buy
# view_response(
#     client.place_order(
#         category="spot",
#         symbol="PORTALUSDT",
#         side="Sell",
#         orderType="Market",
#         qty="1.99",
#         marketUnit="baseCoin"
#     )
# )


# view_response(
#     client.get_open_orders(
#         category="spot"
#     )
# )


# показало что по этому символу я имею "equity": "1.9964", "usdValue": "1.02153791",
# view_response(
#     client.get_wallet_balance(
#         accountType="UNIFIED",
#         coin="PORTAL"
#     )
# )