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
hike_urls = df['URL'].values.tolist()
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

#Set time delay (seconds)
delay = 3
attempt_max = 10

#--------------------------------------------#
#                  Scraper
#--------------------------------------------#

#Create list to append results
hike_data = []

#Start from middle of list to continue script after error
#index_start = 3029
#hike_urls = hike_urls[index_start:len(hike_urls)]

for index, url in enumerate(hike_urls):
    
    #Hike ID
    hike_id = url.rpartition('/')[2]
    
    #Print Status
    print("\n")
    print('Scraping %d of %d pages.........' % (index + 1, len(hike_urls)))
    print('                  Current page:  %s' % (hike_id))
    print('               Remaining pages:  %f' % (len(hike_urls) - (index+1)))
    print('              Percent Complete:  %f' % ((index+1)/len(hike_urls)))
    print('Estimated Time Remaining (hrs):  %f' % ((len(hike_urls) - (index+1))*delay*(1/3600)))
    
    #Request HTLM from webpage
    req = ''
    attempt = 1
    attempt_delay = 5
    while req == '' and attempt <= attempt_max:
        try:
            req = requests.get(url, headers = headers)
            break
        except:
            print("\n")
            print("Connection Error. Trying again in 15 seconds...")
            print("\n")
            attempt = attempt + 1
            sleep(attempt*attempt_delay)
            continue
    if attempt == attempt_max:
        continue
    
    #Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')
    
    if type(soup) is type(None):
        continue
    
    #Further refine soup to the hike wrapper division
    try:
        hike = soup.find('div', attrs = {'id': 'hike-wrapper'})
    except:
        print('    -Could not find hike wrapper')
        continue
    
    if type(hike) is type(None):
        continue
    
    #Hike Name
    key = 'Name'
    try:
        target = hike.find('h1', attrs={'class': 'documentFirstHeading'})
        val = target.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
    
    #Region
    key = 'Region'
    try:
        target = hike.find('div', attrs={'id': 'hike-region'})
        target = target.find('span')
        val = target.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    #Hike Stats (No ID)
    hikestats = hike.find_all('div', attrs={'class':'hike-stat', 'id':''})
    for hikestat in hikestats:
        hikestat_vals = hikestat.find_all('div', attrs={'id':''})
        for i, hikestat_val in enumerate(hikestat_vals):
            try:
                if len(hikestat_vals) == 1:
                    hikestat_header = hikestat.find('h4', attrs={'id':''}).text.strip()
                else: 
                    hikestat_header = hikestat.find('h4', attrs={'id':''}).text.strip() + '_' + str(i)
                key = hikestat_header
                val = hikestat_val.text.strip()
                hike_data.append([hike_id, key, val])
            except:
                print('    -Could not find hike stats')
                
    #Distance
    key = 'Distance'
    try:
        target = hike.find('div', attrs={'id':'distance'})
        val = target.span.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
    
    #Current Rating
    key = 'Rating'
    try:
        target = hike.find('div', attrs={'class':'current-rating'})
        val = target.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
        
    #Rating Count
    key = 'Rating_Count'
    try:
        target = hike.find('div', attrs={'class':'rating-count'})
        val = target.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
    
    #Hike Features
    try:
        target = hike.find('div', attrs={'id':'hike-features'})
        targets = target.find_all('div', attrs= {'class': ['feature alpha ', 'feature ']})
        for feat in targets:
            key = feat.get('data-title')
            val = 'True'
            hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find hike features')
        
    #Permits/Passes
    key = 'Permits'
    try:
        target = hike.find('a', attrs={'title':'Learn more about the various types of recreation passes in Washington'})
        val = target.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
        
    #Alerts
    key = 'Alerts'
    try:
        target = hike.find('div', attrs={'class':'alert orange'})
        val = target.span.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
        
    #Trip Report Count
    key = 'Trip_Report_Cnt'
    try:
        target = hike.find('span', attrs={'class':'ReportCount'})
        val = target.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
        
    #Description
    key = 'Description'
    try:
        target = hike.find('div', attrs={'id':'hike-body-text'})
        val = target.text.strip()
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
        
    #Driving Directions
    key = 'Directions'
    try:
        target = hike.find('div', attrs={'id':'driving-directions'})
        val = ''
        targets = target.find_all('p')
        for target in targets:
            val = val + target.text.strip() + ' '
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
        
    #GPS Coordinates
    try:
        target = hike.find('div', attrs={'class':'latlong'})
        targets = target.find_all('span')
        if len(targets) == 2:
            key = 'Lat'
            val = targets[0].text.strip()
            hike_data.append([hike_id, key, val])
            
            key = 'Long'
            val = targets[1].text.strip()
            hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: GPS Coordinates')
        
    #Trailhead
    key = 'Trailhead'
    try:
        target = hike.find('div', attrs={'id':'trailhead-details'})
        targets = target.find_all('p')
        val = ''
        for target in targets:
            val = val + target.text.strip() + ' '
        hike_data.append([hike_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))
        
    #Time delay before loading next page
    sleep(delay)


df = pd.DataFrame.from_records(hike_data, columns = ['ID', 'Key', 'Value'])
df.to_csv("hike_data_molten.csv", index = False, encoding = "utf-8")
#df_piv = df.pivot(index = 'Hike', columns = 'Key', values = 'Value')


