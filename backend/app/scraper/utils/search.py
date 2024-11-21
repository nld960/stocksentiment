from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import os

def load_drivers():
    global wait, driver_loadall, driver_conditional

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver_loadall = webdriver.Chrome("scraper/chromedriver/chromedriver", options=chrome_options)

    capabilities = DesiredCapabilities.CHROME
    capabilities["pageLoadStrategy"] = "none"

    driver_conditional = webdriver.Chrome("scraper/chromedriver/chromedriver", options=chrome_options, desired_capabilities=capabilities)
    wait = WebDriverWait(driver_conditional, 20)

def get_html(url):
    driver_loadall.get(url)

    html = driver_loadall.page_source
    return html

def get_html_onload(url, element):
    driver_conditional.get(url)
    wait.until(EC.presence_of_element_located(element))
    driver_conditional.execute_script("window.stop();")

    html = driver_conditional.page_source
    return html

load_drivers()

if __name__ == "__main__":
    """
    benchmark of speed between loading entire site 
    and ensuring a specific element is loaded
    """
    import time

    URL = "https://xueqiu.com/S/SH600600"
    t = time.time()
    get_html(URL)
    print(time.time() - t)

    t = time.time()
    html = get_html_onload(URL, (By.CLASS_NAME, "status-list"))
    print(time.time() - t)

    soup = BeautifulSoup(html, "html.parser")
    listing = soup.find("div", class_="status-list")
    for article in listing.find_all("article", class_="timeline__item"):
        print(article, end="\n\n\n")
