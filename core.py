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

    
class FormFilters(ABC):
    """
    Contains all filtering logic to determine which Form 4's to follow.

    Current criteria:

     - Select only stock purchases with transaction code "A" or "P"
     - Select only Stocks bought by officers or directors of the company
     - Select only large purchases (>=50,000 USD Transaction value)

    Parameters:

     - self.parameters_dict = dictionary of parameters to filter from, key = Field, item = list of codes/value)
     - self.unfiltered_dict = incoming dictionary of Form 4 information to be filtered
     - self.filtered_dict = outbound dict of filtered prospective companies
    """

    @abstractmethod
    def filterforms(self):
        """Recieves dict of all new forms, if it is empty, do nothing"""
        pass

class ExecutionHandler(ABC):
    """
    Recieves a list of companies to buy, checks the current account balance, and executes trades according to the defined trading logic.

    Parameters:

     - self.credentials_path = string of where the credentials are located
     - self.take_profit = float value for the take profit percentage (default = 0.2)
     - self.stop_loss = float value for the stop loss percentage (default = 0.07) 
     - self.current_positions = dict of executed trades that day
    """
    @abstractmethod
    def connecttobroker(self, credentials_path):
        """Access credentials txt file and log into broker account"""
        pass

    @abstractmethod
    def definetradinglogic(self):
        """Outlines all relevant trading logic"""
        pass

    @abstractmethod
    def executetrade(self, form_dicts):
        """Recieve most up to date Form 4 dicts and execute trades according to trading logic. Stores recorded trades in csv"""
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
    def pushtradenote(self, trade_info):
        """Push a notification to a live webpage with all trade information according to NEWTRADES bool"""
        pass

    @abstractmethod
    def calculatemetrics(self):
        """Calculates daily win rate, total profit, total loss, amount lost to commissions, PnL"""



