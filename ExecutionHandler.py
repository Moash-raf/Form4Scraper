from core import ExecutionHandler

class IBKRPaper(ExecutionHandler):
    """
    Sub-class specific to handling executing trades using Interactive Broker API with a paper trading account

    Parameters:

     - self.credentials_path = string of where the credentials are located
     - self.take_profit = float value for the take profit percentage (default = 0.2)
     - self.stop_loss = float value for the stop loss percentage (default = 0.07) 
     - self.current_positions = dict of executed trades that day
    """
    def connecttobroker(self, credentials_path):
        """Access credentials txt file and log into broker account"""
        pass

    def definetradinglogic(self):
        """Outlines all relevant trading logic"""
        pass

    def executetrade(self, form_dicts):
        """Recieve most up to date Form 4 dicts and execute trades according to trading logic. Stores recorded trades in csv"""
        pass
