import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pickle
import time
from tqdm import tqdm
import csv

userLogins = []
products = []
item = "laptops"

# Cookies
def save_cookies():
    loaded_cookies = driver.get_cookies()
    pickle.dump(loaded_cookies, open('cookies.txt', "wb"))

def load_cookies():
    cookies = pickle.load(open('cookies.txt', 'rb'))
    return cookies

def getLogins():
    # print("[+] Fetching credetials")
    with open('credentials.csv', 'r') as file:
        csv_reader = csv.DictReader(file, delimiter=",")
        for details in csv_reader:
            userLogins.append(details)

def Login(email, password):
    global wait, driver

    print("[+] Inputing Email:", email)
    email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ap_email"]')))
    email_input.send_keys(email)
    continue_btn = driver.find_element_by_xpath('//*[@id="continue"]')
    continue_btn.click()

    time.sleep(2)

    print("[+] Inputing password:")
    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ap_password"]')))
    password_input.send_keys(password)
    login_btn = driver.find_element_by_xpath('//*[@id="signInSubmit"]')
    login_btn.click()

def signin_page():
    global driver, wait
    # create action chain object
    action = ActionChains(driver)

    # Using action chains 
    accounts_menu = driver.find_element_by_xpath('//*[@id="nav-link-accountList"]')
    signin_menu = driver.find_element_by_xpath('//*[@id="nav-flyout-ya-signin"]/a/span')

    action.move_to_element(accounts_menu)
    time.sleep(3)
    action.click(signin_menu)
    action.perform()

def search_items():
    # Locate Search Bar and send keys
    search_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="twotabsearchtextbox"]')))
    search_bar.send_keys(item)
    search = driver.find_element_by_xpath('//*[@id="nav-search-submit-button"]')
    search.click()

def getPage(source):
    page_items = []
    soup = BeautifulSoup(source, 'lxml')
    main = soup.find('div', class_='s-main-slot s-result-list s-search-results sg-row')
    sections = main.find_all(['div'], class_= "s-include-content-margin s-latency-cf-section s-border-bottom s-border-top")
    for section in sections:
        items = []
        description = section.find('span', class_='a-size-medium a-color-base a-text-normal').string
        rating = "N/A" if section.find('span', class_='a-icon-alt') is None else section.find('span', class_='a-icon-alt').string
        reviews = "N/A" if section.find('span', class_='a-size-base') is None else section.find('span', class_='a-size-base').string
        if section.find('span', class_='a-price-whole') is not None:
            prices = section.find('span', class_='a-price-whole')
            span_tag = prices.span
            span_tag.decompose()
            price = prices.string.replace(',', '')
        else: 
            price = "N/A"
        items.append(description)
        items.append(rating)
        items.append(reviews)
        items.append(price)
        page_items.append(items)
        products.append(items)
    

def write_csv(products):
    with open(f'.\\documents\\{item}.csv', 'w',encoding= "utf-8", newline="") as f:
        headers = ["Product Description", "Rating", "Reviews", "Price"]
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(products)

def next_page():
    global driver, wait
    ul  = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'a-pagination')))
    next = ul.find_element_by_class_name('a-last')
    next.click()
    

if __name__ == "__main__":
    BASE_URL  = "https://www.amazon.com/"
    cd = os.getcwd()
    path = os.path.join(cd,"chromedriver.exe")
    chromeOptions = webdriver.ChromeOptions()
    # prefs = {"download.default_directory": f"{cd}\\Temp"}
    # chromeOptions.add_experimental_option("prefs", prefs)
    chromeOptions.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(path, options=chromeOptions)
    wait = WebDriverWait(driver, 20)

    # Program Execution
    driver.get(BASE_URL)
    getLogins()
    # signin_page()
    print("Starting Scraper")

    for user in userLogins:
        try:
            try:    
                cookies = load_cookies()
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()
            except:
                driver.delete_all_cookies()
                signin_page()
                Login(user['email'], user['password'])
                time.sleep(1)
                save_cookies()      
            search_items()
            time.sleep(1)
            pages_elem  = driver.find_element_by_class_name('a-pagination')
            pages = pages_elem.find_elements_by_tag_name('li')[-2].text
            for page in tqdm(range(1, int(pages)+1), desc="Pages Completion"):
                getPage(driver.page_source)
                next_page()
                time.sleep(2)
            print("[+] working on CSV")
            write_csv(products)
 
        except Exception as e:
            # print("[-] Check your internet connection")
            print(e)

        finally:
            driver.quit()
