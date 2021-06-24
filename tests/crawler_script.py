#! /usr/bin/env python3 
import asyncio
#import aiofiles
#import pickle
from seleniumwire import webdriver #Grab headers/cookies over the wire/network
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException as ENI
import datetime
import os 


#driver and driver options  should be defined in function calling this script.

async def get_headers(driver, app_name, start_url):
    """
    Test.
    Import into main.py 
    Call Asyncronously while data extraction and storage coroutines are running.
    """
    driver.get(start_url) #Initialize webdriver
    print("Initiated at: ", datetime.datetime.now())
    #Search google for appstore
    print("Loading page...")
    try:
        search = driver.find_element_by_id("ac-gn-link-search")
        search.click()
        await asyncio.sleep(5)
    except:
        print("Loading...")
        await asyncio.sleep(25)
        search = driver.find_element_by_id("ac-gn-link-search")
        search.click()
        await asyncio.sleep(2)
    search_app = driver.find_element_by_id("ac-gn-searchform-input")
    search_app.send_keys(app_name) #Pass user input into search bar.
    await asyncio.sleep(2)
    search_app.send_keys(Keys.RETURN) #Search for app/company
    print("Searching for app. Standby...")
    print("Crawling appstore...")
    await asyncio.sleep(10) #Wait for search results to load
    try:
        view_more = driver.find_element_by_class_name("as-links-name").click() #Click first result
    except NoSuchElementException:
        print("Error; refreshing page.")
        driver.refresh() #Refresh
        await asyncio.sleep(30)
        view_more = driver.find_element_by_class_name("as-links-name").click()

    print("Accessing app page")
    await asyncio.sleep(10)
    #See all reviews button isn't always rendered in view for selenium to click.
    try:
        show_all = driver.find_elements_by_class_name("section__nav__see-all-link")
        show_all[1].click()
    except ENI or IndexError: #Element not interactable
        try:
            driver.refresh() 
            print("Driver refreshed") 
            await asyncio.sleep(10) #Try waiting longer for element to render.
            show_all = driver.find_elements_by_class_name("section__nav__see-all-link")
            show_all[1].click()
        except ENI:
            driver.refresh() #If the element is rendered but isn't in view; try refreshing the page and scrolling down.
            await asyncio.sleep(10)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #Scroll down to locate element
            show_all = driver.find_elements_by_class_name("section__nav__see-all-link") 
            show_all[1].click() #Click see all reviews button.

    await asyncio.sleep(5) #wait to ensure that the script below loads the url for requesting reviews.
    try:
        get_headers.total_reviews = driver.find_element_by_css_selector("div.we-customer-ratings__count").text #Grab total num of reviews from page.  Need to preprocess. 
    except NoSuchElementException: #Could also be in <p> tag as opposed to a <div>.  
        driver.refresh()
        await asyncio.sleep(15)
        get_headers.total_reviews = driver.find_element_by_css_selector("p.we-customer-ratings__count").text
    
    print("Total number of reviews: ", get_headers.total_reviews) 
        
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #Scroll down to invoke xhr request for rendering more reviews
    print("Grab url headers for requesting reviews")
    #Grab url for review page.
    await asyncio.sleep(5)
    get_headers.url = driver.last_request.url #Extract review page url
    print(get_headers.url) 
#    async with aiofiles.open(f"./cookies/{app_name}.pkl",'wb') as f:
#        cookie = pickle.dumps([cookie for cookie in cookies])
#        await f.write(cookie) 
    get_headers.headers = driver.last_request.headers #Extract headers from xhr request.  
    #Clear driver cookies and refresh page to generate cookie for review page.
    driver.delete_all_cookies()
    driver.refresh()
    await asyncio.sleep(10) 
    get_headers.cookies = driver.get_cookies() #CookieJar object 
    return driver.quit() #Tear down browser.
