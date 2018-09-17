import os.path
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium import webdriver
import datetime
import time as clock
from random import random
from datetime import datetime

isPayPal = 0
checkedListings = []
sizeC = 0
keywords = []
matchedClothes = []
LOGFILE = True
useConfig = False
password = ''
manualSize = True

peu = {'Visa':'visa', 'American Express':'american_express', 'Mastercard':'master', 'Solo':'solo', 'PayPal':'paypal'}
pasia = {'Visa':'visa', 'American Express':'american_express', 'Mastercard':'master', 'JCB':'jcb', '代金引換':'cod'}
ceu = {'GB':'UK', 'UK (N. IRELAND)':'NB', 'AUSTRIA':'AT', 'BELARUS':'BY', 'BELGIUM':'BE', 'BULGARIA':'BG',
        'CROATIA':'HR', 'CZECH REPUBLIC':'CZ', 'DENMARK':'DK', 'ESTONIA':'EE', 'FINLAND':'FI', 'FRANCE':'FR',
        'GERMANY':'DE', 'GREECE':'GR', 'HUNGARY':'HU', 'ICELAND':'IS', 'IRELAND':'IE', 'ITALY':'IT',
        'LATVIA':'LV', 'LITHUANIA':'LT', 'LUXEMBOURG':'LU', 'MONACO':'MC', 'NETHERLANDS':'NL', 'NORWAY':'NO',
        'POLAND':'PL', 'PORTUGAL':'PT', 'ROMANIA':'RO', 'RUSSIA':'RU', 'SLOVAKIA':'SK', 'SLOVENIA':'SI',
        'SPAIN':'ES', 'SWEDEN':'SE', 'SWITZERLAND':'CH', 'TURKEY':'TR'}

class Found(Exception):
    pass


def pause():
    clock.sleep(random())

def check_exists_by_xpath(xpath, driver):
    try:
        return driver.find_element_by_id(xpath[9:-2])
    except NoSuchElementException:
        myElem = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_element_by_xpath(xpath)

def sendKeys(value, field, driver):
    if len(value) < 1:
        return None
    try:
        driver.execute_script("arguments[0].value = '" + value + "';", field)
    except WebDriverException:
        return None


def selectValue(value, obj):
    try:
        obj.select_by_value(value)
    except WebDriverException:
        pass


def getLoc(f):
    base_path = os.path.abspath(".")
    return os.path.join(base_path, f)


def writeLog(txt):
    if not LOGFILE:
        return None
    f = open(getLoc('logfile.txt'), 'a')
    f.write(str(txt) + '\n')
    f.close()


def cart():
    cart = driver.find_elements_by_class_name('checkout')[0]
    cart.click()

    name = check_exists_by_xpath("""//*[@id="order_billing_name"]""", driver)
    sendKeys(paydetails['Name'], name, driver)

    email = check_exists_by_xpath("""//*[@id="order_email"]""", driver)
    sendKeys(paydetails['Email'], email, driver)

    phone = check_exists_by_xpath("""//*[@id="order_tel"]""", driver)
    sendKeys(paydetails['Phone'], phone, driver)

    add1 = check_exists_by_xpath("""//*[@id="bo"]""", driver)
    sendKeys(paydetails['Addr1'], add1, driver)

    add2 = check_exists_by_xpath("""//*[@id="oba3"]""", driver)
    sendKeys(paydetails['Addr2'], add2, driver)

    if reg != 'ASIA':
        country = Select(driver.find_element_by_name("order[billing_country]"))
    if reg == 'EU':
        selectValue(ceu[paydetails['Country']], country)
    elif reg == 'US':
        selectValue(paydetails['Country'], country)

    if reg == 'EU':
        add3 = check_exists_by_xpath("""//*[@id="order_billing_address_3"]""", driver)
        sendKeys(paydetails['Addr3'], add3, driver)
    elif reg == 'US':
        state = Select(driver.find_element_by_name("order[billing_state]"))
        selectValue(paydetails['Addr3'], state)

    city = check_exists_by_xpath("""//*[@id="order_billing_city"]""", driver)
    sendKeys(paydetails['City'], city, driver)

    postcode = check_exists_by_xpath("""//*[@id="order_billing_zip"]""", driver)
    sendKeys(paydetails['Post/zip code'], postcode, driver)

    if reg == 'EU' or reg == 'ASIA':
        cardType = Select(driver.find_element_by_id("credit_card_type"))
        if reg == 'EU':
            selectValue(peu[paydetails['CardType']], cardType)
        else:
            selectValue(pasia[paydetails['cardType']], cardType)

    if paydetails['CardType'].lower() != 'paypal' or paydetails['CardType'] != '代金引換':
        if reg == 'EU':
            cardno = check_exists_by_xpath("""//*[@id="cnb"]""", driver)
        elif reg == 'US':
            cardno = check_exists_by_xpath("""//*[@id="nnaerb"]""", driver)
        sendKeys(paydetails['Cardno'], cardno, driver)

        if reg == 'EU':
            cvv = check_exists_by_xpath("""//*[@id="vval"]""", driver)
        elif reg == 'US':
            cvv = check_exists_by_xpath("""//*[@id="orcer"]""", driver)
        sendKeys(paydetails['CardCVV'], cvv, driver)

        expiraryDate1 = Select(driver.find_element_by_name("credit_card[month]"))
        selectValue(paydetails['CardMonth'], expiraryDate1)

        expiraryDate2 = Select(driver.find_element_by_name("credit_card[year]"))
        selectValue(paydetails['CardYear'], expiraryDate2)

    tickBox = driver.find_elements_by_class_name('iCheck-helper')
    tickBox[1].click()

    complete = driver.find_element_by_name('commit')
    complete.click()


def searchItem(item):
    url = 'http://www.supremenewyork.com/shop/all/'
    url += item['selectedCategory']
    driver.get(url)

    try:
        while True:
            bestMatch = [0, 0, 0]
            driver.get(url)

            listings = driver.find_elements_by_class_name("name-link")
            leng = len(listings)
            for i in range(0, leng):
                if i % 2 == 0:
                    text = listings[i].text
                    split = text.strip()
                    matches = 0
                    colour = 0
                    for keyword in item['keywords']:
                        if keyword.encode('ascii', 'ignore') in split.encode('ascii', 'ignore'):
                            matches += 1
                    try:
                        lcolour = listings[i+1].text
                        if lcolour.encode('ascii', 'ignore') in item['selectedColour'].encode('ascii', 'ignore'):
                            colour = 1
                    except AttributeError:
                        colour = 0
                    writeLog([item['keywords'], item['selectedColour'], split, lcolour, matches,
                              colour, len(item['keywords']) + colour])
                    if len(item['keywords']) == matches and strict:
                        if item['selectedColour'] != '' and colour == 1:
                            listings[i].click()
                            raise Found
                        elif item['selectedColour'] == '' and colour == 0:
                            listings[i].click()
                            raise Found
                    if bestMatch[0] <= matches and colour >= bestMatch[1]:
                        bestMatch[0] = matches
                        bestMatch[1] = colour
                        bestMatch[2] = i
            if not strict:
                break

        listings[bestMatch[2]].click()
    except Found:
        pass

    clock.sleep(0.5+random())

    try:
        if item['selectedSize'] != 'First available' and item['selectedSize'] != '':
            if reg == 'EU':
                size = Select(driver.find_element_by_id("size"))
            elif reg == 'US':
                size = Select(driver.find_element_by_id("s"))
            op = size.options
            found = False
            for x in op:
                if item['selectedSize'] in x.text:
                    found = True
                    break
            if found:
                selectValue(item['selectedSize'], size)
            elif manualSize:
                print('\nSELECTED SIZE NOT FOUND/AVAILABLE MANUAL SELECT\n')
                clock.sleep(3)
            else:
                print("Sorry the item size is sold out!")
                return None

        add = driver.find_element_by_xpath("""//*[@id="add-remove-buttons"]/input""")
        add.click()
    except NoSuchElementException:
        print("Sorry the item is sold out!")
        return None
    pause()

def returnTime():
    timeInput = droptime.split(":")
    tarHour = int(timeInput[0])
    tarMin = int(timeInput[1])
    tarSec = int(timeInput[2])
    target = datetime.now()
    target = target.replace(hour=tarHour, minute=tarMin, second=tarSec)

    while True:
        cur = datetime.now()
        if cur >= target:
            clock.sleep(1)
            break


def openTab(url, driver):
    m = driver.current_window_handle
    try:
        driver.execute_script('''window.open("{0}","_blank")'''.format(url))
    except WebDriverException:
        pass
    driver.switch_to.window(m)


def openChrome(paydetailsO, itemdetsO, timeO, strictO, cdloc, capabilities, useProxy, PROXY):
    global driver, strict, password, reg, items, droptime, pDescr, paydetails, category
    chrome_options = webdriver.ChromeOptions()
    if useProxy:
        prx = Proxy()
        prx.proxy_type = ProxyType.MANUAL
        prx.http_proxy = PROXY
        prx.socks_proxy = PROXY
        prx.ssl_proxy = PROXY
        prx.add_to_capabilities(capabilities)
    else:
        prx = Proxy()
        prx.proxy_type = ProxyType.SYSTEM
        prx.add_to_capabilities(capabilities)

    chrome_options.binary_location = capabilities['chrome.binary']

    driver = webdriver.Chrome(cdloc, desired_capabilities=capabilities)
    openTab('https://www.google.com', driver)
    paydetails = paydetailsO
    reg = paydetailsO['Region']
    strict = strictO
    droptime = timeO
    items = []
    for x in itemdetsO:
        print(x[0],x[1],x[2],x[3])
        items.append({'selectedCategory': x[0], 'keywords': x[1].split(','), 'selectedColour': x[2], 'selectedSize': x[3]})
    returnTime()
    try:
        for it in items:
                searchItem(it)
        cart()
    except (WebDriverException, AttributeError):
        print('[!] Chrome window closed. Click GO! to re-start')
        return None