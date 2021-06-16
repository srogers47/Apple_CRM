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
    total_reviews = [] 
    

    async def crawl_to_app(self, app_name):
        """
        test imported crawler script.  Too long to make OOP 
        Function crawls to app review page and retrieves cookies.
        Cookies are fed into data_extraction coroutines. 
        """
        #Selenium crawler
        #binary = FirefoxBinary('/usr/bin/firefox/firefox')
        options = Options()
        options.headless = True #Change to "False" to view the robot browser crawl.
        driver = webdriver.Firefox(executable_path=r"/usr/local/bin/geckodriver", options=options) #removed path to binary 
        
        await get_headers(driver=driver, app_name=app_name, start_url=self.start_url) #Crawler script 
        self.url = get_headers.url #Base url used for requests. 
        self.headers = get_headers.headers #Headers used for requests.
        self.total_reviews = get_headers.total_reviews 
        print("Cookies, headers, and new url retrieved.") #Cookies stored in pickle
        print(self.headers, self.url, "Total reviews: ",self.total_reviews) #Testing output 

    async def extract_reviews(self, session, i): 
        """
        Check session cookies, and switch cookie if needed. 
        Extract reviews/datapoints from review page.
        Transform into json format.
        """
        pass




    async def fetch(self, app_name):
        """
        Call crawl_to_app return results for fetch data_extraction.
        Data extraction will require on going retrieval of cookies.
        """
        await self.crawl_to_app(app_name) 
        print("Extracting data points") 

    async def fetch_extraction(self): 
        """
        Call data extraction process in parallel to crawl_to_app()
        cookie retrieval.
        Replace cookies when needed.
        """
        with aiohttp.ClientSession(loop=loop) as session:
            cookies = pickle.load(open(f"cookies/{m.app_name}.pk1", "rb")) #Load cookies into session.
            for c in cookie:
                s.cookies.set(c['name'], c['value'], domain=c['domain']) 
            tasks = [self.extract_reviews(session, i) for i in range(10, int(m.offset_num) + 10, 10)]
                #NOTE:#offset_num if all well be reassigned to converted num found on review page.
            results = await asyncio.gather(*tasks) #Gather tasks as coroutines.
        
    
if __name__=='__main__':    
    m = Main()  
    loop = asyncio.get_event_loop() 
    app_name = "doximity"  #input("Name of app: ") #Testing 
    results = loop.run_until_complete(m.fetch(app_name)) 
    print(results) #test

