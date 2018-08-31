import os.path
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
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

peu = {'Visa':'visa', 'American Express':'american_express', 'Mastercard':'master', 'Solo':'solo', 'Paypal':'paypal'}
pasia = {'Visa':'visa', 'American Express':'american_express', 'Mastercard':'master', 'JCB':'jcb', '代金引換':'cod'}
ceu = {'GB':'UK', 'UK (N. IRELAND)':'NB', 'AUSTRIA':'AT', 'BELARUS':'BY', 'BELGIUM':'BE', 'BULGARIA':'BG',
        'CROATIA':'HR', 'CZECH REPUBLIC':'CZ', 'DENMARK':'DK', 'ESTONIA':'EE', 'FINLAND':'FI', 'FRANCE':'FR',
        'GERMANY':'DE', 'GREECE':'GR', 'HUNGARY':'HU', 'ICELAND':'IS', 'IRELAND':'IE', 'ITALY':'IT',
        'LATVIA':'LV', 'LITHUANIA':'LT', 'LUXEMBOURG':'LU', 'MONACO':'MC', 'NETHERLANDS':'NL', 'NORWAY':'NO',
        'POLAND':'PL', 'PORTUGAL':'PT', 'ROMANIA':'RO', 'RUSSIA':'RU', 'SLOVAKIA':'SK', 'SLOVENIA':'SI',
        'SPAIN':'ES', 'SWEDEN':'SE', 'SWITZERLAND':'CH', 'TURKEY':'TR'}

def pause():
    clock.sleep(random())

def check_exists_by_xpath(xpath, driver):
    try:
        myElem = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_element_by_xpath(xpath)
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
    loc = os.path.dirname(__file__)
    if len(loc) < 1:
        return f
    return loc + '\\' + f


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
        cardType.select_by_visible_text(paydetails['CardType'])

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

    tickBox = driver.find_element_by_xpath("""//*[@id="cart-cc"]/fieldset/p/label/div/ins""")
    tickBox.click()

    complete = check_exists_by_xpath("""//*[@id="pay"]/input""", driver)
    complete.click()


def searchItem(item):
    url = 'http://www.supremenewyork.com/shop/all/'
    url += item['selectedCategory']
    driver.get(url)

    while True:
        matchedClothes = []
        checkedListings = []
        for x in range(5, 1):
            driver.get(url)

        listings = driver.find_elements_by_class_name("name-link")
        for i in range(0, len(listings), 1):
            if i % 2 != 0:
                text = listings[i - 1].text
                split = text.strip()
                matches = 0
                colour = 0
                for keyword in item['keywords']:
                    if keyword.encode('ascii', 'ignore') in split.encode('ascii', 'ignore'):
                        matches += 1
                try:
                    coloura = listings[i].text
                    if item['selectedColour'].encode('ascii', 'ignore') in coloura.encode('ascii', 'ignore'):
                        colour = 1
                except AttributeError:
                    colour = 0
                if matches != 0:
                    matches += colour
                writeLog([item['keywords'], item['selectedColour'], split, item['selectedColour'], coloura, matches, len(item['keywords']) + 1])
                checkedListings.append(matches)
                matchedClothes.append(matches)

        largestMatch = 0
        for i in range(0, len(checkedListings), 1):
            if checkedListings[i] > largestMatch:
                largestMatch = checkedListings[i]
        if item['selectedColour'] != '' and largestMatch == len(item['keywords']) + 1:
            break
        elif item['selectedColour'] == '' and largestMatch == len(item['keywords']):
            break
        elif not strict:
            break

    selectedIndex = 0
    for i in range(0, len(matchedClothes), 1):
        if largestMatch == matchedClothes[i]:
            selectedIndex = i * 2
            writeLog(selectedIndex)

    listings[selectedIndex].click()

    clock.sleep(0.5+random())

    try:
        if item['selectedSize'] != '':
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
    isTime = timeInput[0]
    while True:
        ts = clock.time()
        houra = datetime.fromtimestamp(ts).strftime('%H')
        hour = int(houra)
        if str(hour) >= isTime:
            clock.sleep(1)
            break


def openChrome(paydetailsO, itemdetsO, timeO, strictO, service, capabilities):
    global driver, strict, password, reg, items, droptime, pDescr, paydetails, category
    service.start()
    driver = webdriver.Remote(service.service_url, capabilities)
    paydetails = paydetailsO
    reg = paydetailsO['Region']
    strict = strictO
    droptime = timeO
    items = []
    for x in itemdetsO:
        print(x[0],x[1],x[2],x[3])
        items.append({'selectedCategory': x[0], 'keywords': x[1].split(','), 'selectedColour': x[2], 'selectedSize': x[3]})
    returnTime()
    for it in items:
        searchItem(it)
    cart()
