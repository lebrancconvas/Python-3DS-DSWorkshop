#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import findall,sub
from lxml import html
from time import sleep
from selenium import webdriver
from pprint import pprint
from xvfbwrapper import Xvfb
from selenium.webdriver.chrome.options import Options

searchKey = "Thailand" # Change this to your city 
checkInDate = '27-10-2018' #Format %d-%m-%Y
checkOutDate = '29-10-2018' #Format %d-%m-%Y
url = 'http://www.hotels.com'
n_page = 300

def createResponse(searchKey, checkInDate, checkOutDate, url):
    
    chromedriver = "../scrapping_project/driver/chromedriver.exe"

    """You need to add the argument --headless to invoke Chrome in headless mode.
    For Windows OS systems you need to add the argument --disable-gpu
    As per Headless: make --disable-gpu flag unnecessary --disable-gpu flag is not required on Linux Systems and MacOS.
    As per SwiftShader fails an assert on Windows in headless mode --disable-gpu flag will become unnecessary on Windows Systems too.
    Argument start-maximized is required for a maximized Viewport.
    Here is the link to details about Viewport.
    You may require to add the argument --no-sandbox to bypass the OS security model."""

    # options = Options()
    # options.add_argument("--headless") # Runs Chrome in headless mode.
    # options.add_argument('--no-sandbox') # Bypass OS security model
    # options.add_argument('--disable-gpu')  # applicable to windows os only
    # options.add_argument('start-maximized') # 
    # options.add_argument('disable-infobars')
    # options.add_argument("--disable-extensions")

    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--incognito")

    response = webdriver.Chrome(chrome_options=chrome_options,executable_path=chromedriver) # Driver = webdriver.Chrome()
    response.get(url) # driver.get("http://www.python.org")
    body = response.find_element_by_css_selector('body')
    searchKeyElement = response.find_elements_by_xpath('//input[contains(@id,"destination")]')
    checkInElement = response.find_elements_by_xpath('//input[contains(@class,"check-in")]')
    checkOutElement = response.find_elements_by_xpath('//input[contains(@class,"check-out")]')
    submitButton = response.find_elements_by_xpath('//button[@type="submit"]')
    if searchKeyElement and checkInElement and checkOutElement:
        searchKeyElement[0].send_keys(searchKey)
        checkInElement[0].clear()
        checkInElement[0].send_keys(checkInDate)
        checkOutElement[0].clear()
        checkOutElement[0].send_keys(checkOutDate)
        randomClick = response.find_elements_by_xpath('//h1')
        if randomClick:
            randomClick[0].click()
        submitButton[0].click()
        sleep(15)
        dropDownButton = response.find_elements_by_xpath('//fieldset[contains(@id,"dropdown")]')
        if dropDownButton:
            dropDownButton[0].click()
            priceLowtoHigh = response.find_elements_by_xpath('//li[contains(text(),"low to high")]')
            if priceLowtoHigh:
                priceLowtoHigh[0].click()
                sleep(10)
    return response

def phaseAndSave(response, n_page):
    # Scrolls down the page, loading the dynamically generated content on Hotels.com.
    # 600 page downs seems excessive, but I can't figure put how to keep scrolling until no more content is loaded.
    progress = 0
    for num in range(n_page):
        if num == 0:
            response.execute_script("window.scrollTo(0, 3000);")
        if num > 0:
            response.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        progress += 1
        print("progress: ", progress, ": ", n_page)
        sleep(4)
            
    parser = html.fromstring(response.page_source,response.current_url)
    hotels = parser.xpath('//div[@class="hotel-wrap"]')
    for hotel in hotels: #Replace 5 with 1 to just get the cheapest hotel
        hotelName = hotel.xpath('.//h3/a')
        hotelName = hotelName[0].text_content() if hotelName else ""
        price = hotel.xpath('.//div[@class="price"]/a//ins')
        price = price[0].text_content().replace(",","").strip() if price else ""
        if price == None:
            price = hotel.xpath('.//div[@class="price"]/a')
            price = price[0].text_content().replace(",","").strip() if price else ""
        price = findall('([\d\.]+)',price) if price else ""
        price = price[0] if price else ""
        rating = hotel.xpath('.//div[@class="star-rating-text star-rating-text-strong"]')
        rating = rating[0].text_content().split("-star")[0] if rating else ""
        address = hotel.xpath('.//span[contains(@class,"locality")]')
        address = "".join([x.text_content() for x in address]) if address else ""
        locality = hotel.xpath('.//span[contains(@class,"locality")]')
        locality = locality[0].text_content().replace(",","").strip() if locality else ""
        location = hotel.xpath('.//a[@class="map-link xs-welcome-rewards"]')
        location = location[0].text_content() if location else ""
        region = hotel.xpath('.//span[contains(@class,"locality")]')
        region = region[0].text_content().replace(",","").strip() if region else ""
        postalCode = hotel.xpath('.//span[contains(@class,"postal-code")]')
        postalCode = postalCode[0].text_content().replace(",","").strip() if postalCode else ""
        countryName = hotel.xpath('.//span[contains(@class,"country-name")]')
        countryName = countryName[0].text_content().replace(",","").strip() if countryName else ""

        hotel_text = ""
        hotel_text += ( str(hotelName) + "|" 
                        + str(price) + "|" 
                        + str(rating) + "|"
                        + str(location) + "|"
                        + str(region) + "|"
                        + str(postalCode)
                        # + str(address) + "|"
                        # + str(countryName) + ","
                        + "\n" )

        # ส่วน Save Text files            
        with open('../scrapping_project/output-data/sme_project/hotel_com/hotel_thailand_2729.txt', 'a', encoding='utf-8') as out:
            out.write(hotel_text)
        out.close()
        

if __name__ == '__main__':
    # vdisplay = Xvfb()
    # vdisplay.start()
    res = createResponse(searchKey, checkInDate, checkOutDate, url)
    phaseAndSave(res, n_page)
    # vdisplay.stop()