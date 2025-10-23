import requests
import gzip
import io
import csv
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "https://www.sec.gov/Archives/edgar/daily-index"
HEADERS = {"User-Agent": "Bermuda Research team@bermudaresearch.com"}


def get_form4_filings(days_back=180, output_csv="form4_urls.csv"):
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days = days_back)
    current_date = start_date
    results = []
    while current_date <= today:
        year = current_date.year
        quarter = (current_date.month - 1) // 3 + 1
        date_str = current_date.strftime("%Y%m%d")
        url = f"{BASE_URL}/{year}/QTR{quarter}/master.{date_str}.idx"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            url += ".gz"
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code != 200:
                print(f"No index for {date_str}")
                current_date += timedelta(days=1)
                continue

            with gzip.open(io.BytesIO(resp.content), "rt", encoding="latin1") as f:
                lines = f.readlines()
        else:
            lines = resp.text.splitlines()
        start = False
        
        for line in lines:
            if not start:
                if line.startswith("CIK|Company Name|Form Type"):
                    start = True
                continue
            parts = line.strip().split("|")
            if len(parts) < 5:
                continue
            cik, company, form_type, date_filed, filename = parts
            if form_type == "4":
                filing_url = f"https://www.sec.gov/Archives/{filename}"
                results.append({
                    "cik": cik,
                    "company": company,
                    "date": date_filed,
                    "url": filing_url
                })
        
        print(f"Processed {date_str}, found {len([r for r in results if r['date']==date_str])} Form 4 filings")
        current_date += timedelta(days=1)
        time.sleep(0.2)

    # Save results to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["date", "company", "cik", "url"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    
    return results


if __name__ == "__main__":
    filings = get_form4_filings()
    print(len(filings))





