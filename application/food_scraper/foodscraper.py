#from asyncio.windows_events import NULL
import csv
from matplotlib import pyplot as plt
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
import random
import pandas as pd
from ib_insync import *
from dateutil.parser import parse
import time
import pandas as pd
import numpy as np

class urlBuilder:

    def constructURL(fruits):
        # NOTE : Indistinct may not be necessary in almost every case
        # indistinct = '&sxsrf=APq-WBuMTTuCJ6akx6ppvt6G2IZ-i3pc4w%3A1650990755702&ei=ox5oYoPFKpO-tQa7xYGACQ&ved=0ahUKEwjDopXsk7L3AhUTX80KHbtiAJAQ4dUDCA4&uact=5&oq=what+is+an+orange&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEOgcIABBHELADOgoIABBHELADEIsDOgQIIxAnOgUIABCRAjoLCAAQgAQQsQMQgwE6BAgAEEM6CAguEIAEELEDOhEILhCABBCxAxCDARDHARCjAjoLCC4QgAQQsQMQgwE6DgguEIAEELEDEMcBEKMCOggIABCxAxCDAToUCC4QgAQQsQMQgwEQxwEQ0QMQ1AI6CwguEIAEEMcBEKMCOgoIABCxAxCDARBDOggIABCABBDJAzoFCAAQkgM6CAgAEIAEELEDSgUIPBIBM0oECEEYAEoECEYYAFCoBljaFmCnF2gDcAF4AIABb4gBlQySAQM5LjeYAQCgAQHIAQi4AQLAAQE&sclient=gws-wiz'
        
        urls = []
        storage = open('foods.txt', 'w')
        # Google search url builder
        for fruit in fruits:
            base = 'https://www.google.com/search?q=' + 'what+is+an+' + str(fruit) # + indistinct
            storage.writelines(base)
            storage.write('\n')
            urls = urls + [base]
        storage.close()
        return urls
    
    def collectAddresses():
        f = open('foods.txt')
        messyAddressText, addresses = f.readlines(), []
        f.close()
        for line in messyAddressText: addresses = addresses + [line[:len(line)-1]]
        return addresses
    
# Web Scraper Goal : Crawl First Google Page to Gather General Data
# Transcribe dates into our own database that we will translate and publish later
# NOTE : This program was built to APPEND fruit_data.txt which means if ran multiple times with the same paramters will result in data redundancy
class nasdaqScrapy(scrapy.Spider):
    name = 'nasdaqScrapy'
    # We will pull data from Fidelity's dividend calendar
    start_urls = urlBuilder.collectAddresses()

    def start_requests(self):
        i = 0
        while(i < len(self.start_urls)):
            current = self.start_urls[i]
            yield scrapy.Request(url=current, callback=self.parse, 
                headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"})
            i += 1

    def parse(self, response, **iteration):
        # print('RUN----------------------------------------------------------------------------------')
        time.sleep(random.randint(1,6))
        # print('RESPONSE: ' + str(response))
        
        # All data stored in results csv file for simple collection and parsing
        filename = 'results.csv'
        # Header already recorded, but written here for easier reading
        header = ['Query', 'Description']
        with open(filename, 'a+', newline='', encoding='utf-8') as f:
            strResponse = str(response)
            query = scrapyHelpFunctions.grabQuery(strResponse)
            description = response.xpath('//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div/div/div[1]/div/div/div/span[1]/text()').extract()[0]
            if len(description) > 0:
                writer = csv.writer(f)
                row = [query, description]
                writer.writerow(row)

            # print(query)
            # print(description)
    
class scrapyHelpFunctions:
    def grabQuery(strResponse: str):
        # Locate beginning of search
        totalStr = strResponse[strResponse.index('what+is+an+')+11:len(strResponse)-1]
        return totalStr.replace('%20', ' ')

# We have stored the results in a csv file. Now, we need to match them with our requests
def interpretResults(requestedFruits):
    df = pd.read_csv('results.csv', usecols=[0, 1], engine='python')
    df = df.values
    # print(df)
    alignedResult = {}
    for fruit in requestedFruits:
        for line in df:
            # print(line[0])
            if line[0] == fruit:
                # print(line[0])
                alignedResult[fruit] = line[1:]
    return alignedResult

def vehicle(requestedFruits):
    # First, bob builds the urls needed to request information for the following foods
    urlBuilder.constructURL(requestedFruits)
    #time.sleep(5)

    # We begin the process
    process = CrawlerRunner() # testing CrawlerRunner() rather than CrawlerProcess()
    process.crawl(nasdaqScrapy)
    # process.start() # UNCOMMENT IF CrawlerProcess() rather than CrawlerRunner()
    return interpretResults(requestedFruits)
