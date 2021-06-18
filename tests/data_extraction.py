#! /usr/bin/env python3

#selenium
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException as ENI

import datetime
import asyncio 
import aiohttp
#aiofiles #Non-blocking access to .pkl file containing cookies
import pickle
import json

from crawler_script import get_headers  


class Main:
    """
    Test
    """
    url = "" #Use to pass review request url into get_reviews
    headers = [] 
    start_url = "https://www.apple.com/app-store/"    
    num_reviews =  0 #Zero by defualt. 
    missed = [] #Reviews that aren't extracted successfully added to this list.

    async def crawl_to_app(self, app_name, initial_pass):
        """
        test imported crawler script.  Too long to make OOP 
        Function crawls to app review page and retrieves cookies.
        Cookies are fed into data_extraction coroutines. 
        """
        total_reviews = [] #Placeholder for string value 
        #Selenium crawler
        #binary = FirefoxBinary('/usr/bin/firefox/firefox')
        options = Options()
        options.headless = True #Change to "False" to view the robot browser crawl.
        driver = webdriver.Firefox(executable_path=r"/usr/local/bin/geckodriver", options=options) #removed path to binary 
        await get_headers(driver=driver, app_name=app_name, start_url=self.start_url) #Crawler script 
        self.url = get_headers.url #Base url used for requests. 
        self.headers = get_headers.headers #Headers used for requests.
        if initial_pass: 
            total_reviews = get_headers.total_reviews 
            await self.calc_num_reviews(total_reviews) #Only extract/calculate the amount of available reviews once.  
        print("Cookies, headers, and new url retrieved.") #Cookies stored in pickle
        print(self.headers, self.url) #Testing output 


    async def extract_reviews(self, session, i): 
        """
        Check session cookies, and switch cookie if needed. 
        Extract reviews/datapoints from review page.
        Transform into json format.
        """
        #How can i seamlessly pass cookie into session?
        #Temp storage in memory
        reviews = []
        dates = []
        ratings = []
        titles = []
        
        #Format params for get requests 
        params = (
                ('l', 'en-US'),
                ('offset', f'{i}'), 
                ('platform', 'web'),
                ('additionalPlatforms', 'appletv,ipad,iphone,mac'),
    ) 
        async with session.get(self.url) as response:
            temp = response.json()['data'] 
            try:
                await temp #temp json 
                print(i,temp) #testing output
            except KeyError: 
                #pass into array of missed datapoints for retry.
                self.missed.append(i) 
                print("Error retrieving data at offset", i)
            if temp:
                for a in temp: #Extract data points from json  
                    ratings = a['attributes']['rating']
                    reviews = a['attributes']['review']
                    dates = a['attributes']['date']
                    titles = a['attributes']['title']
            

            




        
    async def calc_num_reviews(self, total_reviews):
        """
        Provided an array containing a string representation of all reviews,
        convert string to integer.  
        Only has to be calculated once during extraction.  
        """ 
        total = self.total_reviews.rstrip() 
        total = total[0] #Drop 'Ratings' from string.
        #Check abbreviation.'K' for thousand, or 'M' for million? 
        num = total[:-1] 
        abbrev = total[-1] 
        if abbrev.upper == 'M': 
            self.num_reviews = pow(float(num),7) 
        if abbrev.upper == 'K':
            self.num_reviews = pow(float(num), 3) 

    async def fetch(self, app_name):
        """
        Control/manage retrieval of cookies in parallel to data extraction.
        Cookies expire fast and the crawler on average takes 1.5 minutes to complete one successful traversial. 
        """
        reviews_extracted = 0 #temp counter 
        initial_pass = True
        await fetch_crawl(app_name, inital_pass) 
        await calc_num_reviews(total_reviews) #Calculate the total amount of reviews available to extract.
        num_reviews = input(f"Would you like to extract all {num_reviews} reviews?" ) 
        initial_pass = False #We don't need to calculate 
        #This is tricky 
        while reviews_extracted < num_reviews:  
            await fetch_extraction(reviews_extracted)
            await fetch_crawl(app_name, initial_pass) 
#####

    async def fetch_crawl:(self, app_name):
        """
        Call crawl_to_app return results for fetch data_extraction.
        Data extraction will require on going retrieval of cookies.
        """
        await self.crawl_to_app(app_name) 
        print("Extracting data points") 

    async def fetch_extraction(self, reviews_extracted): 
        """
        Call data extraction process in parallel to crawl_to_app()
        cookie retrieval.
        Replace cookies when needed.
        """
        with aiohttp.ClientSession(loop=loop) as session:
            cookies = pickle.load(open(f"cookies/{m.app_name}.pk1", "rb")) #Load cookies into session.
            for c in cookie:
                s.cookies.set(c['name'], c['value'], domain=c['domain']) 
            tasks = [self.extract_reviews(session, i) for i in range(10, int(num_reviews) + 10, 10)]
            results = await asyncio.gather(*tasks) #Gather tasks as coroutines.
        
    
if __name__=='__main__':    
    m = Main()  
    loop = asyncio.get_event_loop() 
    app_name = "doximity"  #input("Name of app: ") #Testing 
    results = loop.run_until_complete(m.fetch(app_name)) 
    print(results) #test will print none unless reviews are extracted. 

