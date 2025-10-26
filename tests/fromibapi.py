from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def marketDataType(self, reqId, marketDataType):
        # This callback is received when the market data type is changed.
        print(f"Market data type changed to: {marketDataType}")

    def tickPrice(self, reqId, tickType, price, attrib):
        # This callback is where you receive the price updates.
        print(f"ReqId: {reqId}, TickType: {tickType}, Price: {price}")

def run_delayed_data():
    app = IBapi()
    app.connect("127.0.0.1", 7497, 1001) # Connect to TWS/IB Gateway

    # --- Request delayed data ---
    # First, set the market data type to DELAYED.
    app.reqMarketDataType(3)

    # Next, define the contract for the market data. (e.g., Apple stock)
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    # Now, make the market data request. The API will deliver delayed data.
    # The tickPrice callback will receive the information.
    # The 'snapshot' parameter is set to False for streaming data.
    app.reqMktData(1, contract, "", False, False, [])

    # The main loop needs to run to receive data.
    app.run()

run_delayed_data()
