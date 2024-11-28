from pybit.unified_trading import HTTP
import json

from config import API_KEY_BYBIT, API_SECRET_BYBIT


session = HTTP()
print(json.dumps(session.get_instruments_info(
    category="spot",
    symbol="SCUSDT",
), indent=4))


# session = HTTP(
#     testnet=False,
#     api_key=API_KEY_BYBIT,
#     api_secret=API_SECRET_BYBIT,
# )
#
# print(session.place_order(
#     category="spot",
#     symbol="SCUSDT",
#     side="Buy",
#     orderType="Market",
#     qty="0.01"
# ))


session = HTTP(
    testnet=False,
    api_key=API_KEY_BYBIT,
    api_secret=API_SECRET_BYBIT,
)

print(json.dumps(session.amend_order(
    category="spot",
    symbol="SCUSDT",
    qty="0.15"
), indent=4))
