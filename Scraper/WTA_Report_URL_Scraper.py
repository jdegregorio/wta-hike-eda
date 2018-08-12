# -*- coding: utf-8 -*-
"""
WTA Scraper
Author:  Joseph DeGregorio

Description:  This python script gathers all of the trip report page URLs 
from the Washington Trails Association (WTA) webpage (www.wta.org/).

"""
#--------------------------------------------#
#                  Setup
#--------------------------------------------#

#Import Packages/Functions
import requests
import pandas as pd
from bs4 import BeautifulSoup
from numpy import arange
from time import sleep


#Create list to store extracted report URLs
report_urls = []

#--------------------------------------------#
#               Generate Page URLS
#--------------------------------------------#

#Define WTA start URL
url_base = 'https://www.wta.org/@@search_tripreport_listing?b_size=1000&b_start:int='

#Define page increments
url_pages = arange(0, 125000, 1000)

#Print Start
print("\n")
print("Scraping Starting...  now!!!")
print("\n")

for p in list(range(len(url_pages))):
    
    url = url_base + str(url_pages[p])
    
    #--------------------------------------------#
    #           Gather TRIP REPORT URLS
    #--------------------------------------------#
    
    #Request HTLM from webpage
    req = requests.get(url)
    
    #Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')
    
    #Search for all tags containing the report objects
    reports = soup.find_all('div' , attrs={'class': 'item'})
    
    #Check if page is empty
    if len(reports) == 0:
        break
    
    #Extract report URLs
    for i in list(range(len(reports))):
        
        report_urls.append(reports[i].find('a')['href'])
        #print(report_urls[i])
    
    #Print progress
    print("Scraped URLs:  :", len(report_urls))
 
    #Wait 2 seconds before requesting next page
    sleep(2)

#Print Complete
print("\n")
print("Scraping Complete!!!")
print("\n")

#Save report URLs to a csv file for the next phase of scraping
df = pd.DataFrame(report_urls, columns=['URL'])
df.to_csv("report_urls.csv", index = False, encoding = "utf-8")
