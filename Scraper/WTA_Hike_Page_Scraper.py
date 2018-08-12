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
from time import sleep

#Load the list of hike page URLs
df = pd.read_csv("hike_urls.csv", encoding = "utf-8")
hike_urls = df["URL"].values.tolist()
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

#Set time delay (seconds)
delay = 6

#--------------------------------------------#
#                  Scraper
#--------------------------------------------#

#Create list to append results
hike_data = []

#Temporarily shorten list of URLS for debugging
hike_urls = hike_urls[30:35]

for index, url in enumerate(hike_urls):
    #Print Status
    print('Scraping %d of %d pages.........' % (index + 1, len(hike_urls)))
    print('               Remaining pages:  %f' % (len(hike_urls) - (index+1)))
    print('              Percent Complete:  %f' % ((index+1)/len(hike_urls)))
    print('Estimated Time Remaining (hrs):  %f' % ((len(hike_urls) - (index+1))*delay*(1/3600)))
    
    #Request HTLM from webpage
    req = requests.get(url, headers = headers)
    
    #Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')
    
    #Further refine soup to the hike wrapper division
    hike = soup.find('div', attrs = {'id': 'hike-wrapper'})
    
    #Hike Name
    target = hike.find('h1', attrs={'class': 'documentFirstHeading'})
    if str(target) != 'None':
        name = target.text.strip()
    
    #Region
    key = 'Region'
    target = hike.find('div', attrs={'id': 'hike-region'}).find('span')
    if str(target) != 'None':
        val = target.text.strip()
        hike_data.append([name, key, val])
    
    #Hike Stats (No ID)
    hikestats = hike.find_all('div', attrs={'class':'hike-stat', 'id':''})
    for hikestat in hikestats:
        hikestat_vals = hikestat.find_all('div', attrs={'id':''})
        for i, hikestat_val in enumerate(hikestat_vals):
            if len(hikestat_vals) == 1:
                hikestat_header = hikestat.find('h4', attrs={'id':''}).text.strip()
            else: 
                hikestat_header = hikestat.find('h4', attrs={'id':''}).text.strip() + '_' + str(i)
            key = hikestat_header
            val = hikestat_val.text.strip()
            hike_data.append([name, key, val])
    
    #Distance
    key = 'Distance'
    target = hike.find('div', attrs={'id':'distance'}).span
    if str(target) != 'None':
        val = target.text.strip()
        hike_data.append([name, key, val])
    
    #Current Rating
    key = 'Rating'
    target = hike.find('div', attrs={'class':'current-rating'})
    if str(target) != 'None':
        val = target.text.strip()
        hike_data.append([name, key, val])
    
    #Rating Count
    key = 'Rating_Count'
    target = hike.find('div', attrs={'class':'rating-count'})
    if str(target) != 'None':
        val = target.text.strip()
        hike_data.append([name, key, val])
    
    #Hike Features
    features = hike.find('div', attrs={'id':'hike-features'}).find_all('div', attrs= {'class': ['feature alpha ', 'feature ']})
    for feat in features:
        key = feat.get('data-title')
        val = True
        hike_data.append([name, key, val])
    
    #Permits/Passes
    key = 'Permits'
    target = hike.find('a', attrs={'title':'Learn more about the various types of recreation passes in Washington'})
    if str(target) != 'None':
        val = target.text.strip()
        hike_data.append([name, key, val])
    
    #Alerts
    key = 'Alerts'
    target = hike.find('div', attrs={'class':'alert orange'})
    if str(target) != 'None':
        val = target.span.text.strip()
        hike_data.append([name, key, val])
    
    #Trip Report Count
    key = 'Trip_Report_Cnt'
    target = hike.find('span', attrs={'class':'ReportCount'})
    if str(target) != 'None':
        val = target.text.strip()
        hike_data.append([name, key, val])
    
    #Description
    key = 'Description'
    target = hike.find('div', attrs={'id':'hike-body-text'})
    if str(target) != 'None':
        val = target.text.strip()
        hike_data.append([name, key, val])
    
    #Driving Directions
    key = 'Directions'
    targets = hike.find('div', attrs={'id':'driving-directions'}).find_all('p')
    val = ''
    if str(targets) != 'None':
        for target in targets:
            val = val + target.text.strip() + ' '
        hike_data.append([name, key, val])
    
    #GPS Coordinates
    latlong = hike.find('div', attrs={'class':'latlong'}).find_all('span')
    if str(latlong) != 'None':
        if len(latlong) == 2:
            key = 'Lat'
            val = latlong[0].text.strip()
            hike_data.append([name, key, val])
            
            key = 'Long'
            val = latlong[1].text.strip()
            hike_data.append([name, key, val])
    
    #Trailhead
    key = 'Trailhead'
    val = ''
    targets = hike.find('div', attrs={'id':'trailhead-details'}).find_all('p')
    for target in targets:
        val = val + target.text.strip() + ' '
    hike_data.append([name, key, val])
    
    #Teme delay before loading next page
    sleep(delay)


df = pd.DataFrame.from_records(hike_data, columns = ['Hike', 'Key', 'Value'])
#df.to_csv("hike_data.csv", index = False, encoding = "utf-8")


