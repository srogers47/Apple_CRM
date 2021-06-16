#! /usr/bin/env python3

#selenium
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException as ENI

import datetime
import asyncio 
#aiofiles #Non-blocking access to .pkl file containing cookies
import pickle

from crawler_script import get_headers  #test import crawler as function 

#NOTE: In order to replicate test, create a dir "cookies/" within this dir tests/.  
#I have excluded it from this repo for security purposes.  

class Main:
    """
    Test seleniumwire as co-routine.  
    Crawl store for provided app.
    Collect cookies and store in pickle.
    Use exp time on cookies for naming. 
    """
    #Provided offset num must be divisable by 10. 
    #offset_num = input("Provide number of reviews to scrape or type 'ALL': ") 
    #if "," in [offset_num]: offset_num = str(offset_num).strip(",") #Remove commas 
    url = "" #Use to pass review request url into get_reviews
    headers = [] 
    start_url = "https://www.apple.com/app-store/"    
    

    async def crawl_to_app(self, app_name):
        """
        test imported crawler script.  Too long to make OOP 
        Function crawls to app review page and retrieves cookies.
        Cookies are fed into data_extraction coroutines. 
        """
        #Selenium crawler
        options = Options()
        options.headless = True #Change to "False" to view the robot browser crawl.
        driver = webdriver.Firefox(executable_path=r"/usr/local/bin/geckodriver", options=options)
        
        await get_headers(driver=driver, app_name=app_name, start_url=self.start_url) #Crawler script 
        self.url = get_headers.url #Base url used for requests. 
        self.headers = get_headers.headers #Headers used for requests. 
        print("Cookies, headers, and new url retrieved.") #Cookies stored in pickle
        print(self.headers, self.url) #Testing output 




    async def fetch(self, app_name):
        """
        Call crawl_to_app return results for fetch data_extraction.
        Data extraction will require on going retrieval of cookies.
        """
        await self.crawl_to_app(app_name) 
        print("Test complete.") 
        return print("Extracting data") #place holder for data extraction call 
        
    
if __name__=='__main__':    
    m = Main()  
    loop = asyncio.get_event_loop() 
    app_name = "doximity"  #input("Name of app: ") #Testing 
    results = loop.run_until_complete(m.fetch(app_name)) 
    print(results) #test

