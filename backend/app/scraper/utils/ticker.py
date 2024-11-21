"""
Util for stock tickers, including:
- Search for a ticker by name (via Xueqiu for now)
- Getting prefix of ticker (for use in URL slug)
"""

from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .search import get_html, get_html_onload

URL = "https://xueqiu.com/k?q={}#/stock"

prefixes = {
    "6": "SH",
    "9": "SH",
    "0": "SZ",
    "2": "SZ",
    "3": "SZ",
    "8": "BJ",
}
ALL_PREFIXES = list(set(prefixes.values()))

def is_valid_ticker(string):
    """
    check if ticker is in format "<prefix><numbers>"
    """
    pattern = r'^(' + '|'.join(ALL_PREFIXES) + r')\d{5,6}$'
    match = re.match(pattern, string)
    return match is not None

def get_url_slug(ticker: str, driver):
    if is_valid_ticker(ticker):
        return ticker

    if ticker.isnumeric():
        if len(ticker) == 6:
            return prefixes.get(ticker[0], "") + ticker
        elif len(ticker) == 5:
            return ticker # hk, us
    else:
        if ticker.endswith(".hk"):
            return ticker.removesuffix(".hk") # hk
        elif ticker.endswith(".us"):
            return ticker.removesuffix(".us")
        else:
            # stock name provided
            result = get_ticker(ticker, driver)
#            if re.match(r"^[A-Za-z]{2}\d{5,6}$", result):
#                return result[2:]
            return result

def get_ticker(stock_name: str, driver):
    url = URL.format(stock_name)
    raw_html = get_html_onload(url, (By.CLASS_NAME, "search__stock__bd__code"))
    soup = BeautifulSoup(raw_html, "html.parser")

    results_table = soup.find("table", class_="search__stock__bd")
    matches = []

    for row in results_table.find_all("tr"):
        cols = row.find_all("td")

        if len(cols) == 0:
            continue

        stock_ref = cols[0].find("a")
        name, ticker = stock_ref.find_all("p")
        name_t = name.text.strip()
        ticker_t = ticker.text.strip()

        if name_t == stock_name:
            return ticker.text.strip() # return if exact match found
        else:
            res = {
                "name": name_t,
                "ticker": ticker_t
            }
            matches.append(res)

    return matches
