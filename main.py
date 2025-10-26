import time
import traceback
from datetime import datetime
from FormParser import Form4Parser
from ExecutionHandler import IBKRPaperExecutionHandler

def main():
    formhandler = Form4Parser()
    exechandler = IBKRPaperExecutionHandler()

    hourly_filtered_filings = formhandler.update_filtered(min_value = 1000, transaction_codes = ["S", "D"])
    exechandler.run_trading_cycle(hourly_filtered_filings)
    

if __name__ == "__main__":
    main()