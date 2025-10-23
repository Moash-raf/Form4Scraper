from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

class IBapi(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
    
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.next_order_id = orderId
        print(f"Next valid order ID: {orderId}")
    
    def accountSummary(self, reqId, account, tag, value, currency):
        print(f"Account Summary. {tag}: {value} {currency}")

    def run_loop(app):
        app.run()

app = IBapi()
app.connect("127.0.0.1", 7497, clientId = 1)

api_thread = threading.Thread(target=app.run_loop(), args=(app,), daemon=True)
api_thread.start()

time.sleep(2)

app.reqAccountSummary(1, "ALL", "$LEDGER")

# Defining contract

contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.exchange = "SMARK"
contract.currency = "USD"

# Defining order

order = Order()
order.action = "BUY"
order.orderType = "MKT"
order.totalQuantity = 1

# Placing order

app.placeOrder(app.next_order_id, contract, order)
app.next_order_id += 1

app.disconnect()