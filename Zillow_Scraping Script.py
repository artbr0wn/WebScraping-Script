import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup


# --------------------------------------------------- WEB LINKS ----------------------------------------------------- #

ZILLOW_LINK = "https://www.zillow.com/brooklyn-new-york-ny/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22north%22%3A40.739135%2C%22east%22%3A-73.833552%2C%22south%22%3A40.570842%2C%22west%22%3A-74.041878%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Afalse%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A37607%2C%22regionType%22%3A17%7D%5D%7D"
GOOGLE_FORM_LINK = "https://forms.gle/oV4fQHadtj4kSXDd6"
GOOGLE_FORM_RESPONSE = "https://docs.google.com/forms/d/e/1FAIpQLSdQlyYBnXqLYCQReMNrQ6Mzp7L1xAWkW9ymZ4oixS5lx7AY1A/formResponse"

ADDRESS_XPATH = '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input'
PRICE_XPATH = '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input'
URL_XPATH = '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input'
SUBMIT_XPATH = '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span'

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

# -------------------------------------------------- HTML Parsing --------------------------------------------------- #

# pulling the html from the weblink -- have to use the headers to ensure the bot gets access to Zillow
RESPONSE = requests.get(ZILLOW_LINK, headers=HEADERS)
HTML = RESPONSE.text

# all information for running selenium, ignoring exceptions as they have come up sometimes when locating an element
IGNORED_EXCEPTIONS = (NoSuchElementException, StaleElementReferenceException,)
OPTIONS = webdriver.ChromeOptions()
# selenium options in case I want to see the webpage remain open after it finishes its run through
OPTIONS.add_experimental_option("detach", True)
driver = webdriver.Chrome()
driver.get(GOOGLE_FORM_LINK)


# lines 37-68 used functions as it was more visible -- decided to future-proof script for other information if necessary
# these functions were to grab all necessary data from HTML link (addy,url,price) & return respective list w/ data
def grab_address_data(website_html):

    soup = BeautifulSoup(website_html, 'html.parser')
    anchors = soup.select(selector=".photo-cards_extra-attribution a")
    address_data = [
        x.get_text().replace("                                                                ", " ")
        .replace("\n                                                            \n", " ")
        .strip("\n")
        .replace("\n", " ")
        .rstrip()
        for x in anchors[::2]
    ]

    return address_data


def grab_url_data(website_html):

    soup = BeautifulSoup(website_html, 'html.parser')
    anchors = soup.select(selector=".photo-cards_extra-attribution a")
    url_data = [x.get("href") for x in anchors[::2]]

    return url_data


def grab_price_data(website_html):

    soup = BeautifulSoup(website_html, "html.parser")
    prices_tag = soup.select(selector=".iMKTKr")
    price_data = [x.text.replace("/mo", "").lstrip("$") for x in prices_tag]

    return price_data


# lines 72-142 used functions as it was more visible
# these functions were to use selenium to check if fields were available and return T/F if not,
# These were used specifically b/c I kept running into a problem where each find_element function wouldn't allow for DOM
# to load -- so now each function runs a wait.until func that allows for the DOM to load first
# and I can pinpoint which function is not working via timeout with exception handling.

def find_address():

    try:
        WebDriverWait(driver, timeout=30, ignored_exceptions=IGNORED_EXCEPTIONS) \
            .until(ec.element_to_be_clickable((By.XPATH, ADDRESS_XPATH)))

    except TimeoutError:
        print("Website has timed out while finding address")

    finally:
        address_find = driver.find_element(By.XPATH, ADDRESS_XPATH)

    if address_find.text == "":
        return True
    else:
        return False


def find_url():

    try:
        WebDriverWait(driver, timeout=30, ignored_exceptions=IGNORED_EXCEPTIONS) \
            .until(ec.element_to_be_clickable((By.XPATH, URL_XPATH)))

    except TimeoutError:
        print("Website has timed out while finding url")

    finally:
        url_find = driver.find_element(By.XPATH, URL_XPATH)

    if url_find.text == "":
        return True
    else:
        return False


def find_price():

    try:
        WebDriverWait(driver, timeout=30, ignored_exceptions=IGNORED_EXCEPTIONS) \
            .until(ec.element_to_be_clickable((By.XPATH, PRICE_XPATH)))

    except TimeoutError:
        print("Website has timed out while finding price")

    finally:
        price_find = driver.find_element(By.XPATH, PRICE_XPATH)

    if price_find.text == "":
        return True
    else:
        return False


def find_submit():

    try:
        WebDriverWait(driver, timeout=30, ignored_exceptions=IGNORED_EXCEPTIONS) \
            .until(ec.element_to_be_clickable((By.XPATH, SUBMIT_XPATH)))

    except TimeoutError:
        print("Website has timed out")

    finally:
        submit_button_ = driver.find_element(By.XPATH, SUBMIT_XPATH)

    if submit_button_.text == "Submit":
        return True
    else:
        return False


# the legs of the script -- I decided to find by XPath as it was the most straightforward option.

address_list = grab_address_data(website_html=HTML)
price_list = grab_price_data(website_html=HTML)
url_list = grab_url_data(website_html=HTML)


for entry in range(len(address_list)):

    if find_address():
        address_entry = driver.find_element(By.XPATH, ADDRESS_XPATH)
        address_entry.send_keys(address_list[entry])
    else:
        print("Failed to find address textbox")

    if find_url():
        url_entry = driver.find_element(By.XPATH, URL_XPATH)
        url_entry.send_keys(url_list[entry])
    else:
        print("Failed to find url textbox")

    if find_price():
        price_entry = driver.find_element(By.XPATH, PRICE_XPATH)
        price_entry.send_keys(price_list[entry])
    else:
        print("Failed to find price textbox")

    if find_submit():
        submit_button = driver.find_element(By.XPATH, SUBMIT_XPATH)
        submit_button.click()
    else:
        print("Failed to find submit button")

    print(f"Entry {entry + 1} submitted: \n {address_list[entry]} | {price_list[entry]} | {url_list[entry]} \n")

    response = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
    response.click()

