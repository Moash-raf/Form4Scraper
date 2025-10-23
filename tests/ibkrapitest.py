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
        