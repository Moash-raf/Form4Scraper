from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.ticktype import TickTypeEnum
import threading
import time
from datetime import datetime, timedelta
import pytz


class IBapi(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.last_close = 0
    
    def nextValidId(self, orderId: OrderId):
        self.orderId = orderId
    
    def nextId(self):
        self.orderId += 1
        return self.orderId
    
    def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
        print(f"ReqID: {reqId}, errorCode: {errorCode}, errorString: {errorString}, orderReject: {advancedOrderReject}")

    def tickPrice(self, reqId, tickType, price, attrib):
        print(f"ReqID: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, price: {price}, attribute: {attrib}")
        self.last_close = price if TickTypeEnum.to_str(tickType) in ["DELAYED_CLOSE", "CLOSE"]  else self.last_close
    
    def tickSize(self, reqId, tickType, size):
        print(f"ReqID: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, size: {size}")


app = IBapi()
app.connect("127.0.0.1", 7497, 0)
threading.Thread(target=app.run).start()
time.sleep(1)

contract = Contract()
contract.symbol = "ADMA"
contract.secType = "STK"
contract.exchange = "SMART"
contract.currency = "USD"

start_date = datetime.now(pytz.timezone('US/Eastern')) - timedelta(days = 0)
start_date_str = start_date.strftime("%Y%m%d %H:%M:%S") + " US/Eastern"


app.reqMarketDataType(3)
app.reqMktData(app.nextId(), contract, "232", False, False, [])
time.sleep(5)
print(f"Last known close is {app.last_close}")
time.sleep(2)
app.disconnect()



    

    
# #     def tickPrice(self, reqId, tickType, price, attrib):
# #         """Store latest price based on request ID"""
        
# #         print(f"tickPrice: reqId={reqId}, tickType={tickType}, price={price}")
        
# #         if not hasattr(self, "market_data"):
# #             self.market_data = {}
        
# #         if reqId not in self.market_data:
# #             self.market_data[reqId] = {}

# #         if tickType == 4:
# #             self.market_data[reqId]["last"] = price
# #         if tickType == 1:
# #             self.market_data[reqId]["bid"] = price
# #         if tickType == 2:
# #             self.market_data[reqId]["ask"] = price

# #     def get_latest_price(self, contract, timeout=5):
# #         """
# #         Returns the most recent market price for a contract.
# #         - During market hours: last traded price or delayed price.
# #         - Outside market hours: last close price from historical snapshot.
# #         """
# #         # US stock market hours: 9:30–16:00 ET (Eastern)
# #         print("Requesting market price")
# #         est = timezone("US/Eastern")
# #         now_est = datetime.datetime.now(est)
# #         market_open = now_est.replace(hour=9, minute=30, second=0, microsecond=0)
# #         market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)

# #         # Check if today is weekday
# #         is_weekday = now_est.weekday() < 5

# #         if is_weekday and market_open <= now_est <= market_close:
# #             # --- Market open: request delayed/live price ---
# #             self.reqMarketDataType(3)  # delayed data if no real-time subscription
# #             reqId = int(time.time() * 1000) % 100000
# #             if not hasattr(self, "market_data"):
# #                 self.market_data = {}
# #             self.market_data[reqId] = {}

# #             self.reqMktData(reqId, contract, "", False, False, [])

# #             start = time.time()
# #             price = None
# #             while time.time() - start < timeout:
# #                 ticks = self.market_data[reqId]
# #                 if 'last' in ticks:
# #                     price = ticks['last']
# #                     break
# #                 elif 'bid' in ticks and 'ask' in ticks:
# #                     price = (ticks['bid'] + ticks['ask']) / 2
# #                     break
# #                 time.sleep(0.05)

# #             self.cancelMktData(reqId)

# #             if price is None:
# #                 print(f"No market data received for {contract.symbol} during market hours")
# #             return price

# #         else:
# #             # --- Market closed: get last close via historical data ---
# #             reqId = int(time.time() * 1000) % 100000
# #             self.hist_data = []

# #             self.reqHistoricalData(
# #                 reqId=reqId,
# #                 contract=contract,
# #                 endDateTime='',
# #                 durationStr='2 D',      # last 2 trading days to ensure data
# #                 barSizeSetting='1 day',
# #                 whatToShow='TRADES',
# #                 useRTH=1,
# #                 formatDate=1,
# #                 keepUpToDate=False,
# #                 chartOptions=[]
# #             )

# #             # Wait for historical data callback
# #             start = time.time()
# #             while len(self.hist_data) == 0 and time.time() - start < timeout:
# #                 time.sleep(0.1)

# #             if len(self.hist_data) == 0:
# #                 print(f"No historical data for {contract.symbol}, cannot provide price")
# #                 return None

# #             # Last bar's close is the last known price
# #             last_close = self.hist_data[-1]['close']
# #             print(f"Market closed: using last close price for {contract.symbol} = {last_close}")
# #             return last_close
    
#     def get_historical_last_2_days(self, contract, timeout=10):
#         """
#         Requests the past 2 days of daily bars for a given contract from TWS.
#         Returns a list of dicts with OHLCV data.
#         """
#         self.hist_data = []  # reset historical data

#         req_id = int(time.time() * 1000) % 100000

#         self.reqHistoricalData(
#             reqId=req_id,
#             contract=contract,
#             endDateTime='',            # now
#             durationStr='2 D',         # last 2 trading days
#             barSizeSetting='1 day',    # daily bars
#             whatToShow='TRADES',
#             useRTH=1,                  # regular trading hours
#             formatDate=1,              # return as YYYYMMDD
#             keepUpToDate=False,
#             chartOptions=[]
#         )

#         # Wait for historical data callback
#         start = time.time()
#         while len(self.hist_data) < 1 and time.time() - start < timeout:
#             time.sleep(0.1)

#         if len(self.hist_data) == 0:
#             print(f"No historical data received for {contract.symbol}")
#             return None

#         return self.hist_data

    
# # def accountSummary(self, reqId, account, tag, value, currency):
# #     print(f"Account Summary. {tag}: {value} {currency}")


# def run_loop(app):
#     app.run()

# app = IBapi()
# app.connect("127.0.0.1", 7497, clientId = 1)

# api_thread = threading.Thread(target=run_loop, args=(app,), daemon=True)
# api_thread.start()


# # app.reqAccountSummary(1, "All", "$LEDGER")

# # Defining contract

# contract = Contract()
# contract.symbol = "AAPL"
# contract.secType = "STK"
# contract.exchange = "SMART"
# contract.currency = "USD"

# # Defining order

# # order = Order()
# # order.action = "BUY"
# # order.orderType = "MKT"
# # order.totalQuantity = 2
# # order.eTradeOnly = False
# # order.firmQuoteOnly = False

# # Requesting market data

# historical = app.get_historical_last_2_days(contract)
# if historical:
#     for bar in historical:
#         print(bar)


# # def make_order(contract, trade_order):
# #     app.placeOrder(app.next_order_id, contract, trade_order)
# #     app.next_order_id +=1
# #     return()

# # make_order(contract, order)

# # while not hasattr(app, "next_order_id"):
# #     time.sleep(0.1)

# # app.next_order_id += 1

# # time.sleep(2)

# # latest_price = app.get_latest_price(contract)
# # print(f"Latest price for {contract.symbol} is {latest_price}")

# app.disconnect()