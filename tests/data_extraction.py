#!/usr/bin/env python3

#selenium
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException as ENI

import datetime
import asyncio 
import aiohttp #Non-blocking requests
#import aiofiles #Non-blocking local file processes 
#import pickle
import json
import os 

from crawler_script import get_headers  


class Main:
    """
    Test
    """
    url = "" #Use to pass review request url into get_reviews
    headers = [] 
    start_url = "https://www.apple.com/app-store/"    
    fresh_cookies = [] #Temp data structure.  Will extract from list to pass cookie dictionary into aiohttp.ClientSession() 
    missed = [] #Reviews that aren't extracted successfully added to this list. Used in data_storage.py
    num_reviews = []         

    async def crawl_to_app(self, app_name, initial_pass):
        """
        Imported crawler script.  
        Function crawls to app review page and retrieves cookies.
        Cookies are fed into data_extraction coroutines. 
        """
        total_reviews = [] #Placeholder for string value 
        #Selenium crawler
        #binary = FirefoxBinary('/usr/bin/firefox/firefox')
        options = Options()
        options.add_argument('--window-size=1920,1080') #Selenium will raise error in headless (as-links-name won't render, can't locate)  unless window size is specified.
        options.headless = True #Change to "False" to view the robot browser crawl. Helpful when debugging. 
        driver = webdriver.Firefox(executable_path=r"/usr/local/bin/geckodriver", options=options) #set path to geckodriver.  On windows append ".exe" to path.
        await get_headers(driver=driver, app_name=app_name, start_url=self.start_url) #Crawler script 
        self.url = get_headers.url #Base url used for requests. 
        self.headers = get_headers.headers #Headers used for requests.
        self.fresh_cookies = get_headers.cookies #CookieJar object extracted from crawl
        if initial_pass: 
            total_reviews = get_headers.total_reviews 
            await self.calc_num_reviews(total_reviews) #Only extract/calculate the amount of available reviews once.  
        print("Cookies, headers, and new url retrieved.") #Cookies stored in pickle
        print(self.headers, self.url, self.fresh_cookies) #Testing output 
        


    async def extract_reviews(self, session, i): 
        """
        Check session cookies, and switch cookie if needed. 
        Extract reviews/datapoints from review page.
        ###Transform into json format.
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
        async with session.get(self.url, headers=self.headers, params=params) as response:
            print(f"Response: {response}") 
            temp = await response.json() 
            try:
                temp = temp['data'] #temp json 
                print(i,temp) #testing output
            except KeyError: 
                #pass into array of missed datapoints for retry.
                self.missed.append(i) 
                print("Error retrieving data at offset", i)
                asyncio.sleep(2) #Test
            if temp:
                for a in temp: #Extract data points from json  
                    ratings = a['attributes']['rating']
                    reviews = a['attributes']['review']
                    dates = a['attributes']['date']
                    titles = a['attributes']['title']
                #Store in dictionary
                temp_dict = { 
                        "Rating": ratings,
                        "Review Content": review,
                        "Date": dates,
                        "Title": titles
                        }
                print(temp_dict) #test output
                                
            
        
    async def calc_num_reviews(self, total_reviews):
        """
        Provided an array containing a string representation of all reviews,
        convert string to integer.  
        Only has to be calculated once during extraction.  
        """ 
        total = total_reviews.split() 
        total = total[0] #Drop 'Ratings' from string.
        print(total) #Delete print statements 
        #Check abbreviation.'K' for thousand, or 'M' for million? 
        num = total[:-1] #Numbers
        print(num)
        abbrev = total[-1] #Abbreviation
        print(abbrev)
        if abbrev == "M": 
           self.num_reviews.append(pow(int(float(num)), 7)) #Wrap float in int to avoid raising value errors.
        if abbrev == "K":
           self.num_reviews.append(pow(int(float(num)), 3)) 
        print(f"Estimated {self.num_reviews[0]} can be extracted") 
        return self.num_reviews


    async def fetch(self, app_name):
        """
        Control/manage retrieval of cookies in parallel to data extraction.
        Cookies expire fast and the crawler on average takes 1.5 minutes to complete one successful traversial. 
        """
        start = 10 #Start at 10.   
        reviews_extracted = 1000 
        initial_pass = True
        await self.fetch_crawl(app_name, initial_pass) 
        #num_reviews = input(f"Would you like to extract all {num_reviews} reviews?" ) 
        initial_pass = False #We don't need to calculate after initial pass
        #Run the tasks concurrently, but prioritize retrieval of request headers/cookie.  
        while reviews_extracted < int(self.num_reviews[0]):  
            await self.fetch_extraction(start, reviews_extracted, app_name)
            await self.fetch_crawl(app_name, initial_pass) 
            if reviews_extracted == 5000: #Testing 
                break 
            start += 1000 #Update start
            reviews_extracted += 1000 #Extract reviews by grouping of this value.  
        print(f"{reviews_extracted} have been extracted.") 
        

    async def fetch_crawl(self, app_name, initial_pass):
        """
        Call crawl_to_app return results for fetch data_extraction.
        Data extraction will require on going retrieval of cookies.
        """
        await self.crawl_to_app(app_name, initial_pass) 


    async def fetch_extraction(self, start, reviews_extracted, app_name): 
        """
        Session restarts with every iteration in fetch.
        Pass in cookies.
        Process is not seamless and entirely relies on duration of crawler task. 
        Optimize crwaler_script before production!
        """
        del self.fresh_cookies[0]['path'] #Remove path from cookies. Well raise error if included due aiohttp prohibitting path being set in session. 
        del self.fresh_cookies[0]['domain'] #The same goes for domain.  
        del self.fresh_cookies[0]['secure'] #and secure.
        del self.fresh_cookies[0]['httpOnly'] #remove just about everything but name and value...
        del self.fresh_cookies[0]['sameSite'] #This code is for instructive purposes. In production simply extract name and value.

        #async with aiofiles.open(f"./cookies/{app_name}.pkl", 'rb') as f: #Load cookies into session. Use context manager to close file after cookie is set. 
            #cookie = await f.read()
            #cookie = pickle.loads(cookie) #Unpickle/Deserialize 
            #assert os.stat(f"./cookies/{app_name}.pkl").st_size > 0 #Test. If the write was unsuccessful, pickle file will be empty and error will be raised.  
        async with aiohttp.ClientSession(loop=loop, cookies=self.fresh_cookies[0]) as session: #Set session cookies
            tasks = [self.extract_reviews(session, i) for i in range(int(start), int(reviews_extracted), 10)] #Prep extraction 
            results = await asyncio.gather(*tasks) #Run gathered tasks 
        
    
if __name__=='__main__':    
    m = Main()  
    loop = asyncio.get_event_loop() 
    app_name = "doximity"  #input("Name of app: ") #Testing 
    results = loop.run_until_complete(m.fetch(app_name)) 
    print(results) #test will print none unless reviews are extracted. 
    print(missed) #Debugging 

