from abc import ABC, abstractmethod

"""
The SEC adds Form 4 submisssions to it's EDGAR Database on a rolling basis from 6AM to 10PM on weekdays.

This Abstract file outlines the blueprint for a Form 4 web scraper that tracks all insider stock purchases, filters them, and sets trading notifications.
"""

class FormParser(ABC):
    """
    Responsible for updating and collecting all relecant Form 4 information for the day.

    Parameters:

     - self.URL_path - String of seen URLs
     - self.start_time - Datetime object dictating when to start requesting forms (default = 6AM on weekdays)
     - self.end_time - Datetime object dictating when to stop requesting forms (default = 10PM on weekdays)
     - self.update_interval - Update interval in minutes
     - self.new_url_list - List of all Form 4 URLs added within update interval
     - self.form_dict - Dictionary of all Form 4 submission data within interval
     - self.new_filings - BOOL value indicating if any filings were made during the last update interval (default = FALSE)
    """

    @abstractmethod
    def fetch_recent_form4(self):
        """Requests last 100 Form 4 filings from EDGAR database and returns URL List with timestamp"""
        pass

    @abstractmethod
    def update_daily_urls(self):
        """Compares last list of URLs to incoming list of URLs. Returns unique, un-duplicated list of most recent Form 4 data with timestamps"""
        pass
    @abstractmethod
    def unpack_urls(self):
        """Converts atom feed of URLs into filing data. Returns list of dicts of filing information"""
        pass
    @abstractmethod
    def filter_filings(self):
        """Recieves filing data, filters only to ones that have been bought by officer or director, have minimum value, and have specific transaction code"""
        pass
    @abstractmethod
    def clear_forms(self):
        """Clears all saved data from data directory"""
    @abstractmethod
    def update_filtered(self):
        """Returns most recent 100 Form 4 filings as dicts based on filter criteria"""
        pass
    @abstractmethod
    def update_unfiltered(self):
        """Returns most recent 100 form 4 filings as dicts"""

class ExecutionHandler(ABC):
    """
    Recieves a list of companies to buy, checks the current account balance, and executes trades according to the defined trading logic.

    Broker connection and sell/buy loops will be handled in main runner function.

    Parameters:

     - self.credentials_path = string of where the credentials are located
     - self.take_profit = float value for the take profit percentage (default = 0.2)
     - self.stop_loss = float value for the stop loss percentage (default = 0.07) 
     - self.daily_orders_filled = dict of executed trades that day
     - self.daily_orders_sent = dict of orers sent but not filled that day
    """

    @abstractmethod
    def define_trading_logic(self):
        """Recieves hourly Form 4 filings to trade. Returns orders with all relevant trading logic."""
        pass
    @abstractmethod
    def match_daily_executions(self):
        """Eliminates existing Orders submitted that day from hourly order feed. Ensures no duplicate orders are done"""
        pass
    @abstractmethod
    def execute_trade(self):
        """Recieve most up to date order and contract objects and execute trades according to trading logic. Stores recorded trades in csv"""
        pass

class ReportingHandler(ABC):
    """
    Records all executed trades, optionally send notifications daily for trades. Calculates key metrics.

    Parameters:

     - self.new_trades = boolean signalling that new trades have taken place during the last update interval
     - self.portfolio_value = float value from broker API
     - self.daily_trades = dict showing all daily trades executed
     - self.trade_log_path = string pointing to where to save trade logs daily
    """
    
    @abstractmethod
    def push_trade_note(self):
        """Push a notification to a live webpage with all trade information according to NEWTRADES bool"""
        pass
    @abstractmethod
    def send_daily_log(self):
        """Requests daily trade log of all submitted and filled trades and returns a list of traded symbols"""
        pass
    @abstractmethod
    def summarize_day_trades(self):
        """Creates a daily report of all trades performed that day"""
        pass
    @abstractmethod
    def summarize_unfiltered_form_4_filings(self):
        """Creates a list of dicts of all Form 4 filings submitted that day"""
        pass
    @abstractmethod
    def calculate_metrics(self):
        """Calculates daily win rate, total profit, total loss, amount lost to commissions, PnL"""



