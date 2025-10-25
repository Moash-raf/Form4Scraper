from core import ExecutionHandler
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import *
import threading
import time
import json
import os
from datetime import datetime, date

# Defining the IBApp object for broker connection

class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.next_order_id = None
        self.connected_flag = False
        self.market_data = {}
    
    def tickPrice(self, reqId, tickType, price, attrib):
        """Updates price in real time"""
        if tickType == 4:
            self.market_data[reqId] = price
 
    def get_live_price(self, contract, timeout=5):
        """Requests and returns the most recent live price for a contract."""
        reqId = int(time.time()) % 100000  # simple unique ID
        self.reqMktData(reqId, contract, "", False, False, [])
        start = time.time()
        while reqId not in self.market_data:
            if time.time() - start > timeout:
                self.cancelMktData(reqId)
                raise TimeoutError(f"Live price request for {contract.symbol} timed out.")
            time.sleep(0.2)
        price = self.market_data[reqId]
        time.sleep(0.2)
        self.cancelMktData(reqId)
        return price

    def nextValidId(self, orderId):
        """TWS callback giving the next order ID available"""
        self.next_order_id = orderId
        self.connected_flag = True
        print(f"[IBApp] Connected. Next valid order ID: {orderId}")
    
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        """Catch and print any API error messages"""
        print(f"[IBApp ERROR] ID: {reqId}, Code: {errorCode}, Msg: {errorString}")
    
    def connectionClosed(self):
        """Notification when IBApp disconnects"""
        self.connected_flag = False
        print("[IBApp] Connection closed")
    
# Defining actual Trading Execution handler class

class IBKRPaperExecutionHandler(ExecutionHandler):
    """
    Sub-class specific to handling executing trades using Interactive Broker API with a paper trading account

    Parameters:

     - self.take_profit = float value for the take profit percentage (default = 0.2)
     - self.stop_loss = float value for the stop loss percentage (default = 0.07) 
     - self.daily_orders_filled = dict of executed trades that day
     - self.daily_orders_sent = dict of orers sent but not filled that day

    """

    def __init__(self, take_profit = 0.1, stop_loss = 0.05):

        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.daily_orders_log = []
        self.app = None
        self.client_id = 1
        self.host = "127.0.0.1"
        self.port = 7497
        self.api_thread = None
        self.order_id_lock = threading.Lock()
        self.connected_flag = False
        self.logs_dir = os.path.join("logs")
        self.today = date.today().strftime("%Y_%m_%d")

        print("Initialized IBKRPaperExecutionHandler Instance")

    def connecttobroker(self):
        """Establish app object, and log into broker account"""
        print("Connecting to IB TWS")

        self.app = IBApp()
        self.app.connect(self.host, self.port, self.client_id)

        # Dedicate separate thread to run TWS API event loop

        self.api_thread = threading.Thread(target=self.app.run, daemon=True)
        self.api_thread.start()

        # Wait for connection to be established
        
        timeout = 10
        start = time.time()
        while not self.app.connected_flag:
            if time.time() - start > timeout:
                raise TimeoutError("Connection to TWS timed out.")
            time.sleep(0.2)

        self.connected_flag = True
        print("Successfully connected to TWS")

    def define_trading_logic(self, filtered_filings):
        """Recieves hourly Form 4 filings to trade. Returns orders with all relevant trading logic."""
        
        trade_orders = []

        for filing in filtered_filings:
            symbol = filing["symbol"]
            transaction_value = filing["shares"]*filing["price"]
            
            # Defining order quantity based on filing transaction value
            
            if transaction_value >= 250000:
                order_qty = 100
            elif transaction_value >= 50000:
                order_qty = 5
            elif transaction_value >= 10000:
                order_qty = 2
            else:
                order_qty = 1


            # Create a contract object for filing

            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"

            # Fetch live market price

            try:
                current_price = self.app.get_live_price(contract)
            except TimeoutError as e:
                print(f"Cannot fetch live price for symbol: {symbol}, {e}")
                continue

            # Define stop loss & take profit values

            stop_loss_price = round(current_price*(1-self.stop_loss), 2)
            take_profit_price = round(current_price*(1+self.take_profit), 2)
            oca_group = f"{symbol}_{int(time.time())}"

            # Create parent order for market entry

            parent_order = Order()
            parent_order.action = "BUY"
            parent_order.orderType = "MKT"
            parent_order.totalQuantity = order_qty
            parent_order.tif = "GTC"
            parent_order.transmit = False

            # Create stop loss order

            stop_loss_order = Order()
            stop_loss_order.action = "SELL"
            stop_loss_order.orderType = "LMT"
            stop_loss_order.lmtPrice = stop_loss_price
            stop_loss_order.totalQuantity = order_qty
            stop_loss_order.ocaGroup = oca_group
            stop_loss_order.ocaType = 1
            stop_loss_order.transmit = False

            # Create take profit order

            take_profit_order = Order()
            take_profit_order.action = "SELL"
            take_profit_order.orderType = "LMT"
            take_profit_order.lmtPrice = take_profit_price
            take_profit_order.totalQuantity = order_qty
            take_profit_order.ocaGroup = oca_group
            take_profit_order.ocaType = 1
            take_profit_order.transmit = True

            # Generate trade data file for future reporting

            trade_data = {
                "symbol" : symbol,
                "current_price" : current_price,
                "stop_loss_price" : stop_loss_price,
                "take_profit_price" : take_profit_price,
                "order_qty" : order_qty
            }

            trade_orders.append((contract, parent_order, stop_loss_order, take_profit_order, trade_data))
        
        print(f"Generated {len(trade_orders)} to be submitted.")

        return trade_orders

    def execute_trade(self, trade_orders):
        """Recieve most up to date order and contract objects and execute trades according to trading logic. Stores recorded trades in csv"""
        
        if not self.connected_flag or not self.app:
            raise ConnectionError("Not connected to TWS")
        
        if not trade_orders:
            print("No trades to execute")
            return
        
        log_path = os.path.join(self.logs_dir, f"executed_trades_{self.today}.json")

        executed_trades = []
        order_count = 0

        for contract, parent_order, stop_loss_order, take_profit_order, trade_data in trade_orders:
            try:
                
                # Wait until next valid order ID comes in

                while self.app.next_order_id is None:
                    time.sleep(0.1)
                
                # Assigning order IDs to OCA group
                with self.order_id_lock:
                    parent_id = self.app.next_order_id
                    self.app.next_order_id += 1
                    stop_loss_id = self.app.next_order_id
                    self.app.next_order_id += 1
                    take_profit_id = self.app.next_order_id
                    self.app.next_order_id += 1

                stop_loss_order.parentId = parent_id
                take_profit_order.parentId = parent_id

                #Placing order & logging it in trade_data

                self.app.placeOrder(parent_id, contract, parent_order)
                self.app.placeOrder(stop_loss_id, contract, stop_loss_order)
                self.app.placeOrder(take_profit_id, contract, take_profit_order)

                trade_data.update({
                    "order_id" : parent_id,
                    "status" : "SENT",
                    "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                executed_trades.append(trade_data)

                order_count += 1
                time.sleep(0.5)

            except Exception as e:
                print(f"Unable to execute order for {trade_data['order_qty']} shares of {trade_data['symbol']}: {e}")
            
            print(f"Executed {len(executed_trades)} trades")

        try:
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    daily_logs = json.load(f)
                daily_logs.extend(executed_trades)
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(daily_logs, f, indent=2, ensure_ascii=False)

            else:
                with open(log_path, "x", encoding="utf-8") as f:
                    json.dump(executed_trades, f, indent=2, ensure_ascii=False)
            
            print(f"Added {len(executed_trades)} new trades to daily log")

        except Exception as e:
            print(f"Cannot log trades to directory {log_path}: {e}")


