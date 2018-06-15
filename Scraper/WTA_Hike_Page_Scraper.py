# -*- coding: utf-8 -*-
"""
WTA Hike Page Scraper
Author: Joseph DeGregorio
Created:Thu Jun 14 20:46:30 2018

Description:  This python script gathers all of the hike page information 
from the Washington Trails Association (WTA) webpage (www.wta.org/). This
script leverages a previously scraped list of hike URLs.

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

#Load the list of hike page URLs
df = pd.read_csv("hike_urls.csv", encoding = "utf-8")
hike_urls = df["URL"].values.tolist()

url = hike_urls[1]

#Request HTLM from webpage
req = requests.get(url)

#Create Soup
soup  = BeautifulSoup(req.text, 'html.parser')

#Search for HIKE NAME
name = soup.find('h1', attrs={'class': 'documentFirstHeading'}).text
region = soup.find('div', attrs={'id': 'hike-region'}).find('span').text
distance = soup.find('div', attrs={'id' : 'distance'}).text[1:-1]


stats = soup.find_all('div', attrs={'class': 'hike-stat'})


