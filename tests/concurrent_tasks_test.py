#!/usr/bin/env python3

#Test: simulate crawling and passing in cookie to data extraction concurrently.
#NOTE: This is NOT a completely seamless process.  
#Crawl must finish before more than 1,000 reviews are extracted; ie an estimate of when cookies expire. 

import asyncio 

class Main:
    async def crawl(self):
        """This will take a minute"""
        print("Waiting")
        await asyncio.sleep(30)
        cookie = "test cookie retrieved" 
        print("Crawl complete", cookie) 

    async def extract(self, i): #i=offset number
        """This will be lightning fast"""
        await asyncio.sleep(5)
        print(f"Request {i} completed") 

    async def fetch(self): 
        """Prioritize tasks"""
        offset = 1000 
        num_reviews = 5001 
        while offset < num_reviews: #Until all reviews have been extracted. 
            await self.crawl() #The crawl needs to finish before more requests can be made.
            task = [self.extract(i) for i in range(offset)] #Simulate sending  requests
            await asyncio.gather(*task) 
            offset += 1000


if __name__=='__main__': 
    m = Main() 
    loop = asyncio.get_event_loop() 
    results = loop.run_until_complete(m.fetch()) 
    print(results) 
    
