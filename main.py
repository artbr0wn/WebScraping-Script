import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import time

# --------------------------------------------------- WEB LINKS ----------------------------------------------------- #

ZILLOW_LINK = "https://www.zillow.com/brooklyn-new-york-ny/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C" \
              "%22mapBounds%22%3A%7B%22north%22%3A40.739135%2C%22east%22%3A-73.833552%2C%22south%22%3A40.570842%2C" \
              "%22west%22%3A-74.041878%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Afalse%2C%22filterState%22%3A%7B" \
              "%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fore%22%3A%7B%22value" \
              "%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22" \
              "%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsbo%22%3A%7B%22value%22" \
              "%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C" \
              "%22isListVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A37607%2C%22regionType%22" \
              "%3A17%7D%5D%7D"
GOOGLE_FORM_LINK = "https://forms.gle/oV4fQHadtj4kSXDd6"
GOOGLE_FORM_RESPONSE = "https://docs.google.com/forms/d/e/1FAIpQLSdQlyY" \
                       "BnXqLYCQReMNrQ6Mzp7L1xAWkW9ymZ4oixS5lx7AY1A/formResponse"

headers = {
    'User-Agent': 'Mozilla/5.0'
}


# -------------------------------------------------- HTML Parsing --------------------------------------------------- #

# grabbing html
response = requests.get(url=ZILLOW_LINK, headers=headers)
html = response.text
soup = BeautifulSoup(html, "html.parser")

# Downloaded temp .html file to test code
# with open("Zillow.html") as temp_file:
#     file = temp_file.read()
#     soup = BeautifulSoup(file, "html.parser")


anchors = soup.select(selector=".photo-cards_extra-attribution a")

# grabbing urls for each scraped apt
urls = [x.get("href") for x in anchors[::2]]

# finding the addresses for each apt -- initial formatting was super weird here so had to get rid
addresses = [
    x.get_text().replace("                                                                ", " ")
    .replace("\n                                                            \n", " ")
    .strip("\n")
    .replace("\n", " ")
    .rstrip()
    for x in anchors[::2]
]

# grabbing the prices for each apartment scraped
prices_tag = soup.select(selector=".iMKTKr")
apt_price = [x.text.replace("/mo", "").lstrip("$") for x in prices_tag]

# entering all the information into a Google form to export into Excel

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome()
driver.get(GOOGLE_FORM_LINK)

# needed to wait, as the initial find methods would not work without
try:
    wait = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input'))
    )
except TimeoutError:
    print("Still not working")

# finding the text entry boxes
address_entry = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/'
                                              'div[2]/div/div[1]/div/div[1]/input')

price_entry = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/'
                                            'div/div/div[2]/div/div[1]/div/div[1]/input')

link_entry = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/'
                                           'div/div/div[2]/div/div[1]/div/div[1]/input')

submit_button = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')

# Filling in the text for the text entry boxes
# I kept getting a stale exception error, which basically means that I tried to find the element before the page loaded
# AND the page DOM changed, so that the last xpath isn't really there anymore, well it is, but also is not

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)

for entry in range(len(addresses)):

    address_find = WebDriverWait(driver, timeout=30, ignored_exceptions=ignored_exceptions) \
        .until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]'
                                                         '/div/div[1]/div/div[1]/input')))

    address_entry.send_keys(addresses[entry])
    price_entry.send_keys(apt_price[entry])
    link_entry.send_keys(urls[entry])
    submit_button.click()
    print(f"Entry {entry + 1} submitted: \n {addresses[entry]} | {apt_price[entry]} | {urls[entry]} \n")
    if driver.current_url == GOOGLE_FORM_RESPONSE:
        try:
            wait = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a'))
            )
        except TimeoutError:
            print("The response page timed out")
        response = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
        response.click()
    time.sleep(5)
