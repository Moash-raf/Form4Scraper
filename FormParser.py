from core import FormParser
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import xml.etree.ElementTree as ET
import json
import time
import os
import random
import requests
from datetime import datetime,date

class Form4Parser(FormParser):
    """
    FormParser Subclass to handle daily gathering of SEC Form4 URL's, unpack them, and deliver them as readable dict.
    """

    def __init__(self, base_path="data"):
        self.today = date.today().strftime("%Y_%m_%d")
        self.feed_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&owner=only&count=100&output=atom"
        self.header = {"User-Agent": "Bermuda Research Form4Monitor/1.0 (team@bermudaresearch.com)"}
        self.fetch_delay = 0.2 #delay of 200 milliseconds to avoid request throttling
        self.base_path = base_path
        self.atom_feed_path = os.path.join(base_path, "browse-edgar")
        self.daily_urls_path = os.path.join(base_path, f"daily_urls_{self.today}")
        self.daily_timestamps_path = os.path.join(base_path, f"daily_timestamps_{self.today}")
        self.daily_filings_path = os.path.join(base_path, f"daily_filings_{self.today}.json")
        self.daily_filtered_filings_path = os.path.join(base_path, f"daily_filtered_filings_{self.today}.json")

    def fetch_recent_form4(self):
        """
        Uses selenium to fetch most recent Form 4 data via Atom feed in XML format 
        """
        # Confirming that no browse-edgar files exist

        if os.path.exists(self.atom_feed_path):
            os.remove(self.atom_feed_path)
        
        # Setting up headless browser
        bin_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
        options = Options()
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", os.path.abspath(self.base_path))
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("pdfjs.disabled", True)
        options.set_preference("browser.download.alwaysOpenPanel", False)
        options.set_preference("general.useragent.override", self.header["User-Agent"])
        options.add_argument("--headless")
        options.binary_location = bin_path

        # Setting up webdriver path
        service = Service("geckodriver/geckodriver_32.exe")
        driver = webdriver.Firefox(service=service, options=options)
        
        #Open browser and save Atom feed
        try:
            driver.set_page_load_timeout(10)
            try:
                driver.get(self.feed_url)
            except Exception:
                driver.execute_script("window.stop();")
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching feed: {e}")

        finally:
            driver.quit()
        
        #Access Atom feed and save to self.new_urls & self.new_timestamps
        if not os.path.exists(self.atom_feed_path):
            print(f"Cannot find Atom feed at location: {self.atom_feed_path}")
            return [], []
        
        try:
            tree = ET.parse(self.atom_feed_path)
            root = tree.getroot()
        
        except ET.ParseError as e:
            print(f"Failed to parse Atom feed error: {e}")
            return [], []

        namespace = {"atom" : "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", namespace)
        
        # Preprocessing of entries list:
        #   Remove yesterdays entries
        #   Remove duplicate URLs
        #   Save timestamps
        #   Save URLs

        new_urls = []
        new_timestamps = []

        for entry in entries:
            ts = entry.find("atom:updated", namespace).text
            ts_datetime_object = datetime.fromisoformat(ts)
            # if ts_datetime_object.date() != datetime.today().date():
            #     continue
            
            title = entry.find("atom:title", namespace).text
            if "Issuer" not in title:
                continue 
            
            link_element = entry.find("atom:link", namespace)
            if link_element is not None and "href" in link_element.attrib:
                link = link_element.attrib["href"]
                #Sanity check
                if "Archives" in link:
                    new_urls.append(link)
                    new_timestamps.append(ts_datetime_object if ts_datetime_object is not None else "N/A")
                    
        print(f"Fetched {len(new_urls)} new URLs")

        #Remove the browse-edgar file to avoid naming errors

        try:
            os.remove(self.atom_feed_path)
            print(f"Deleted {self.atom_feed_path} after saving URLs.")
        except Exception as e:
            print(f"Warning: could not delete {self.atom_feed_path}: {e}")

        return new_urls, new_timestamps
    
    def update_daily_urls(self, new_url_list, new_timestamp_list):
        """
        Compares all daily_urls (if any) to new_urls,
        updates (or creates) daily_urls file for the day and returns all unparsed urls.
        """

        updated_urls= []
        updated_timestamps = []

        if os.path.exists(self.daily_urls_path):
            try:
                with open(self.daily_urls_path, "r", encoding="utf-8") as f:
                    daily_urls = json.load(f)
                with open(self.daily_timestamps_path, "r", encoding="utf-8") as f:
                    daily_timestamps = json.load(f)
                    for index, (new_url, ts) in enumerate(zip(new_url_list, new_timestamp_list)):
                        if new_url in daily_urls:
                            continue
                        else:
                            updated_urls.append(new_url)
                            daily_urls.append(new_url)
                            updated_timestamps.append(ts)
                            daily_timestamps.append(ts)
                try:
                    with open(self.daily_urls_path, "w", encoding="utf-8") as f:
                        json.dump(daily_urls, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    print(f"Warning: failed to write updated urls to {self.daily_urls_path}: {e}")
                try:
                    with open(self.daily_timestamps_path, "w", encoding="utf-8") as f:
                        json.dump(daily_timestamps, f, indent=2, ensure_ascii=False, default=str)
                except Exception as e:
                    print(f"Warning: failed to write updated timestamps to {self.daily_timestamps_path}: {e}")
                print(f"Successfully added {len(updated_urls)} to daily_urls & timestamps lists")
                return(updated_urls, updated_timestamps)
            except Exception as e:
                print(f"Error processing URLs: {e}")
                return(new_url_list, new_timestamp_list)
        else:
                try:
                    with open(self.daily_urls_path, "x", encoding="utf-8") as f:
                        json.dump(new_url_list, f, indent=2, ensure_ascii=False)
                    with open(self.daily_timestamps_path, "x", encoding="utf-8") as f:
                        json.dump(new_timestamp_list, f, indent=2, ensure_ascii=False, default=str)
                    print(f"No existing daily_urls file found for {self.today}, creating new file at: {self.daily_urls_path} and timesmps file at: {self.daily_timestamps_path}")
                    return(new_url_list, new_timestamp_list)
                except Exception as e:
                    print(f"No daily_urls file found for {self.today}.Failed to create new file with error: {e}")
                    return(self.new_url_list, self.daily_timestamps_path)
    
    def unpack_urls(self, new_url_list, new_timestamp_list):
        """
        Creates or updates daily_urls.json file and unpacks new Form 4 URLs.
        Adds 0.2–0.5s random delay between requests to avoid throttling.
        Returns a list of parsed Form 4 filing dicts.
        """

        new_filings = []

        # Checking to see if there are any new filings
        if not new_url_list:
            print("No new filings to process.")
            return []
        
        # Unpacking all new URLs into list of dicts
        for index, (new_url, ts) in enumerate(zip(new_url_list, new_timestamp_list)):
            time.sleep(self.fetch_delay + random.uniform(0, self.fetch_delay))
            try:
                if new_url.endswith("-index.htm"):
                    txt_url = new_url.replace("-index.htm", ".txt")
                else:
                    txt_url = new_url

                # Fetching response
                response = requests.get(txt_url, headers={"User-Agent": "Bermuda Research team@bermudaresearch.com"})
                if response.status_code != 200:
                    raise Exception("Failed to fetch filing")

                text = response.text

                # Extract the XML portion
                start = text.find("<XML>")
                end = text.find("</XML>") + len("</XML>")
                xml_content = text[start:end]

                start_idx = xml_content.find("<?xml")
                xml_content_inner = xml_content[start_idx:]  # from XML declaration to end

                def extract_tag(tag):
                    t_start = xml_content_inner.find(f"<{tag}>")
                    t_end = xml_content_inner.find(f"</{tag}>")
                    if t_start != -1 and t_end != -1:
                        inner_content = xml_content_inner[t_start + len(f"<{tag}>"):t_end].strip()
                        if "<value>" in inner_content and "</value>" in inner_content:
                            v_start = inner_content.find("<value>") + len("<value>")
                            v_end = inner_content.find("</value>")
                            return inner_content[v_start:v_end].strip()
                        return inner_content
                    return "N/A"
            
                issuer = extract_tag("issuerName")
                symbol = extract_tag("issuerTradingSymbol")
                owner = extract_tag("rptOwnerName")
                trans_code = extract_tag("transactionCode")
                shares = float(extract_tag("transactionShares"))
                price = float(extract_tag("transactionPricePerShare"))
                is_director = extract_tag("isDirector")
                is_officer = extract_tag("isOfficer")
                title = extract_tag("officerTitle")
                purchased = True if extract_tag("transactionAcquiredDisposedCode") == "A" else False


                filing = {
                    "source_url": new_url,
                    "timestamp": ts.strftime("%Y/%m/%d, %H:%M:%S"),
                    "issuer": issuer,
                    "symbol": symbol,
                    "owner": owner,
                    "transaction_code": trans_code,
                    "shares": shares,
                    "price": price,
                    "is_director": is_director,
                    "is_officer": is_officer,
                    "title": title,
                    "is_purchased": purchased
                    }
            
                new_filings.append(filing)
                print(f"Parsed {new_url}")
            except Exception as e:
                print(f"Error parsing {new_url}: {e}")
                continue
        print(f"Successfully parsed {len(new_filings)} out of {len(new_url_list)} total URLs")

        #Writing updated daily_filings file or creating new one
        if os.path.exists(self.daily_filings_path):
            try:
                with open(self.daily_filings_path, "r", encoding="utf-8") as f:
                    daily_filings = json.load(f)
                daily_filings = daily_filings.append(new_filings)
                with open(self.daily_filings_path, "w", encoding="utf-8") as f:
                    json.dump(daily_filings, f, indent=2, ensure_ascii=False)
                print(f"Added {len(new_filings)} new filings to daily_filings list")
                return new_filings
            except Exception as e:
                print(f"Error updating daily_filings file: {e}")
                return new_filings
        else:
            try:
                with open(self.daily_filings_path, "x", encoding="utf-8") as f:
                    json.dump(new_filings, f, indent=2, ensure_ascii=False)
                print(f"Successfully created new daily_filings list with {len(new_filings)} at: {self.daily_filings_path}")
                return new_filings
            except Exception as e:
                print(f"Failed to create new daily_filings list with error: {e}")
                return new_filings
    
    def filter_filings(self, unfiltered_filing_data, min_value, transaction_codes):
        """Recieves most recent filing data as list of dict. Filters based on trading criteria and saves to daily_filings_{todays_date}.json file while returning list of filtered filings to trade_execution class"""

        new_filtered_filings = []

        # Checking to see if there are any filings to filter
        if not unfiltered_filing_data:
            print("No filings to filter)")
            return []
        
        # Filtering filing data accorting to trading criteria
        for filing in unfiltered_filing_data:
            try:
                transaction_value = filing["shares"] * filing["price"]
                if transaction_value < min_value:
                    continue
                if filing["is_officer"] in ("false", "0")  and filing["is_director"] in ("false", "0"):
                    continue
                if not filing["is_purchased"]:
                    continue
                if filing["transaction_code"] in transaction_codes:
                    continue
                new_filtered_filings.append(filing)
            except Exception as e:
                print(f"Could not filter filing entry: {filing["source_url"]}, error code: {e}")
                
        print(f"Filtered {len(unfiltered_filing_data)} filings down to {len(new_filtered_filings)}")

        if not new_filtered_filings:
            print("No new filings to add")
            return []

        # Updating persistent filtered_filings_data file
        if os.path.exists(self.daily_filtered_filings_path):
            try:
                with open(self.daily_filtered_filings_path, "r", encoding="utf-8") as f:
                    daily_filtered_filings = json.load(f)
                daily_filtered_filings.append(new_filtered_filings)
                with open(self.daily_filtered_filings_path, "w", encoding="utf-8") as f:
                    json.dump(daily_filtered_filings, f, indent=2, ensure_ascii=False)
        
                return new_filtered_filings
            except Exception as e:
                print(f"Error updating daily_filtered_filings file: {e}")
                return new_filtered_filings
        else:
            try:
                with open(self.daily_filtered_filings_path, "x", encoding="utf-8") as f:
                    json.dump(new_filtered_filings, f, indent=2, ensure_ascii=False)
                print(f"Successfully created new daily_filtered_filings list at: {self.daily_filtered_filings_path}")
                return new_filtered_filings
            except Exception as e:
                print(f"Failed to create new daily_filtered_filings list with error: {e}")
                return new_filtered_filings
    
    def clear_forms(self):        
        try:    
            if os.path.exists(self.daily_urls_path):
                os.remove(self.daily_urls_path)
            else:
                print(f"Warning: no file at: {self.daily_urls_path}] to remove")
            
            if os.path.exists(self.daily_timestamps_path):
                os.remove(self.daily_timestamps_path)
            else:
                print(f"Warning: no file at: {self.daily_timestamps_path}] to remove")
            
            if os.path.exists(self.daily_filings_path):
                os.remove(self.daily_filings_path)
            else:
                print(f"Warning: no file at: {self.daily_filings_path}] to remove")
            
            if os.path.exists(self.daily_filtered_filings_path):
                os.remove(self.daily_filtered_filings_path)
            else:
                print(f"Warning: no file at: {self.daily_filtered_filings_path}] to remove")
            
            print("Cleared all data files")

        except Exception as e:
            print(f"Error, failed to clear data files: {e}")

    def update_filtered(self, min_value = 1000, transaction_codes = ["S", "D"]):
        new_urls, new_timestamps = self.fetch_recent_form4()
        updated_urls, updated_timestamps = self.update_daily_urls(new_urls, new_timestamps)
        new_filings = self.unpack_urls(updated_urls, updated_timestamps)
        filtered_filings = self.filter_filings(new_filings, min_value, transaction_codes)

        return filtered_filings
    
    def update_unfiltered(self):
        new_urls, new_timestamps = self.fetch_recent_form4()
        updated_urls, updated_timestamps = self.update_daily_urls(new_urls, new_timestamps)
        new_filings = self.unpack_urls(updated_urls, updated_timestamps)

        return new_filings
