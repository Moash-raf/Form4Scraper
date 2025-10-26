import time
from datetime import datetime
from ExecutionHandler import IBKRPaperExecutionHandler  # <-- update this with your file name

# Dummy but diverse filings to hit all trade tiers
dummy_filings = [
    {"symbol": "AAPL", "shares": 5, "price": 100.00},      # 500 — smallest tier
    {"symbol": "MSFT", "shares": 150, "price": 120.00},    # 18,000 — tier 2
    {"symbol": "NVDA", "shares": 400, "price": 200.00},    # 80,000 — tier 3
    {"symbol": "AMZN", "shares": 2500, "price": 100.00},   # 250,000 — tier 4 (highest)
]

def main():
    print("\n=== Starting TWS Integration Test ===")

    # Initialize handler
    handler = IBKRPaperExecutionHandler()

    # Step 1 — Connect to TWS
    print("\n[1/4] Connecting to broker...")
    handler.connecttobroker()

    # Step 2 — Generate trade logic
    print("\n[2/4] Defining trade logic...")
    trade_orders = handler.define_trading_logic(dummy_filings)

    print(f"\nTrade logic returned {len(trade_orders)} orders.")
    for trade in trade_orders:
        contract, parent, sl, tp, info = trade
        print(f"  • {info['symbol']} | Qty={info['order_qty']} | "
              f"TP={info['take_profit_price']} | SL={info['stop_loss_price']} | "
              f"Current={info['current_price']}")

    # Step 3 — Execute trades
    print("\n[3/4] Executing trades...")
    handler.execute_trade(trade_orders)

    # Step 4 — Verify logs
    print("\n[4/4] Checking execution logs...")
    try:
        log_file = f"logs/executed_trades_{handler.today}.json"
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
        print(f"\nTrade log contents:\n{log_content}")
    except Exception as e:
        print(f"Could not read log file: {e}")

    print("\n=== TWS Integration Test Completed ===")
    print(f"Time finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
