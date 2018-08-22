# -*- coding: utf-8 -*-
"""
WTA Trip Report Scraper
Author: Joseph DeGregorio
Created: 8/12/2018

Description:  This python script gathers all of the hike page information
from the Washington Trails Association (WTA) webpage (www.wta.org/). This
script leverages a previously scraped list of hike URLs.

"""
# -------------------------------------------- #
#                  Setup
# -------------------------------------------- #

# Import Packages/Functions
import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep

# Load the list of hike page URLs
df = pd.read_csv("report_urls.csv", encoding = "utf-8")
report_urls = df['URL'].values.tolist()
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

# Set time delay (seconds)
delay = 3
attempt_max = 10

# -------------------------------------------- #
#                   Scraper
# -------------------------------------------- #

# Create list to append results
report_data = []

# Start from middle of list to continue script after error
#index_start = 70322
#report_urls = report_urls[index_start:len(report_urls)]

for index, url in enumerate(report_urls):

    # Report ID
    report_id = url.rpartition('trip_report.')[2]

    # Print Status
    print("\n")
    print('Scraping %d of %d pages.........' % (index + 1, len(report_urls)))
    print('                  Current page:  %s' % (report_id))
    print('               Remaining pages:  %f' % (len(report_urls) - (index+1)))
    print('              Percent Complete:  %f' % ((index+1)/len(report_urls)))
    print('Estimated Time Remaining (hrs):  %f' % ((len(report_urls) - (index+1))*delay*(1/3600)))

    # Request HTLM from webpage
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

    # Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')

    if type(soup) is type(None):
        continue

    # Further refine soup to the report wrapper division
    try:
        report = soup.find('div', attrs = {'id': 'report-wrapper'})
    except:
        print('    -Could not find report wrapper')
        continue

    if type(report) is type(None):
        continue

    # ReportURL
    key = 'Report_URL'
    val = url
    report_data.append([report_id, key, val])

    # Hike ID (primary key to hike table)
    key = 'HikeID'
    try:
        target = report.find('h1', attrs={'class': 'documentFirstHeading'}).a.get('href')
        val = target.rpartition('/')[2]
        report_data.append([report_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    # Author UserID
    key = 'UserID'
    try:
        target = report.find('span', attrs={'itemprop':'author'}).a.get('href')
        val = target.rpartition('/')[2]
        report_data.append([report_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    # Author Name
    key = 'Author'
    try:
        target = report.find('span', attrs={'itemprop':'author'}).a
        val = target.text.strip()
        report_data.append([report_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    # Report Date
    key = 'ReportDate'
    try:
        target = report.find('span', attrs={'class':'elapsed-time'})
        val = target.get('datetime')
        report_data.append([report_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    # Trip Conditions
    try:
        conditions = report.find_all('div', attrs={'class':'trip-condition'})
        for condition in conditions:
            key = 'Cond_' + condition.h4.text.strip().replace(' ', '')
            val = condition.span.text.strip()
            report_data.append([report_id, key, val])
    except:
        print('    -Could not find trip conditions')

    # Trip Features
    try:
        features = report.find('div', attrs={'id':'trip-features'}).find_all('div')
        for feature in features:
            key = 'Feat_' + feature.get('data-title').replace(' ', '')
            val = 'True'
            report_data.append([report_id, key, val])
    except:
        print('    -Could not find trip features')

    # Trip Report Description
    key = 'ReportBody'
    try:
        target = report.find('div', attrs={'id':'tripreport-body-text'})
        val = target.text.strip()
        report_data.append([report_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    # Trip Report Description
    key = 'ImageCnt'
    try:
        target = report.find_all('div', attrs={'class':'captioned-image'})
        val = len(target)
        report_data.append([report_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    # Report Helpful Count
    key = 'ReportHelpfulCnt'
    try:
        target = report.find('span', attrs={'class':'total-thumbs-up'})
        val = target.text.strip()
        report_data.append([report_id, key, val])
    except:
        print('    -Could not find attribute: %s' % (key))

    # Time delay before loading next page
    sleep(delay)


df = pd.DataFrame.from_records(report_data, columns = ['ID', 'Key', 'Value'])
df.to_csv("../Cleaning/report_data_molten.csv", index = False, encoding = "utf-8")

