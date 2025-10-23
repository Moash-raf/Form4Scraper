from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

class IBapi(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.hist_data = []  # store OHLCV data
    
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.next_order_id = orderId
        print(f"Next valid order ID: {orderId}")
    
    
    def historicalData(self, reqId, bar):
        # Append each bar as a dictionary
        self.hist_data.append({
            "time": bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        })
    
    def accountSummary(self, reqId, account, tag, value, currency):
        print(f"Account Summary. {tag}: {value} {currency}")


def run_loop(app):
    app.run()

app = IBapi()
app.connect("127.0.0.1", 7497, clientId = 1)

api_thread = threading.Thread(target=run_loop, args=(app,), daemon=True)
api_thread.start()

time.sleep(2)

# app.reqAccountSummary(1, "All", "$LEDGER")

# Defining contract

contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.exchange = "SMART"
contract.currency = "USD"

# Defining order

# order = Order()
# order.action = "SELL"
# order.orderType = "MKT"
# order.totalQuantity = 2
# order.eTradeOnly = False
# order.firmQuoteOnly = False

# Requesting market data

req_id = 1
app.reqHistoricalData(
    reqId=req_id,
    contract=contract,
    endDateTime='',          # '' means now
    durationStr= "1 D",       # 1 hour
    barSizeSetting= '1 min',  # 1-minute bars
    whatToShow='TRADES',     
    useRTH=1,                # regular trading hours only
    formatDate=1,
    keepUpToDate=False,       # snapshot only
    chartOptions=[]
)

# app.placeOrder(app.next_order_id, contract, order)
# app.next_order_id += 1

time.sleep(5)

print(app.hist_data)

app.disconnect()