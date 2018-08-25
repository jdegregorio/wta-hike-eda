# -*- coding: utf-8 -*-
"""
WTA Hike Cleaning
Author: Joseph DeGregorio
Created: 8/17/2018

Description:  This python script takes the long format data table
from scraping as input, pivots the data, and cleans each field.

"""
# =============================================================================
#                                   Setup
# =============================================================================

# Load Libraries
import pandas as pd
import numpy as np
import cleanpy
import pandas_summary

# =============================================================================
#                                 Import Data
# =============================================================================
print('Importing Data...', end='')

# Import Hike Data (Molten State)
df_hikes_molten = pd.read_csv('../Data/hike_data_molten.csv', encoding = "utf-8")

print('Complete')
# =============================================================================
#                                Basic Cleaning
# =============================================================================
print('Basic Cleaning...', end='')

# Remove Incomplete Records
df_hikes_molten.dropna(inplace=True)

# Remove Duplicates
df_hikes_molten.drop_duplicates(inplace=True)

# Combine/Fix Elevation Key Variables (scraped data resulted in 3 unique keys)
df_hikes_molten.Key = np.where(df_hikes_molten.Value.str[:6] == 'Gain: ', 'Elevation_Gain', df_hikes_molten.Key)
df_hikes_molten.Key = np.where(df_hikes_molten.Value.str[:15] == 'Highest Point: ', 'Elevation_Peak', df_hikes_molten.Key)

# Pivot Data to tidy/wide format
df_hikes = df_hikes_molten.pivot(index = 'ID', columns = 'Key', values = 'Value')
df_hikes.reset_index(inplace=True)

# Fix Column Names
new_names = {
    'Dogs allowed on leash': 'Dogs_Leashed',
    'Dogs not allowed': 'Dogs_None',
    'Established campsites': 'Campsites',
    'Fall foliage': 'Fall_Foliage',
    'Good for kids': 'Kid_Friendly',
    'Mountain views': 'Mountain_Views',
    'Old growth': 'Old_Growth',
    'Ridges/passes': 'Ridges_Passes',
    'Wildflowers/Meadows': 'Flowers_Meadows',
    'Rating_Count':'Rating_Cnt'
}

df_hikes.rename(columns = new_names, inplace=True)

# Add URL Column
df_hikes['URL'] = 'https://www.wta.org/go-hiking/hikes/' + df_hikes['ID']

print('Complete')
# =============================================================================
#                              Clean Variables
# =============================================================================
print('Cleaning Variables...\n')

#Remove any duplicate columns
cleanpy.dropdupcol(df_hikes)

#Remove text that appears at start/end of record within a column
cleanpy.chopsubstrings(df_hikes, exclude = ['URL'], inplace = True)

#Split/strip text that appears to be categorical from start/end each record in column
cleanpy.splitsubstrings(df_hikes, exclude = ['URL'], nuq_max = 5, inplace = True)
df_hikes.drop(columns = 'Rating_Cnt_end', inplace = True)  #Drop useless column

#Rename and prettify new column
df_hikes.rename(columns = {'Distance_end':'Distance_Type'}, inplace = True)
df_hikes.Distance_Type.replace(['nan', ' miles, roundtrip', ' miles, one-way', ' miles of trails'],
                               [np.nan, 'Roundtrip', 'One-way', 'Total Trail'],
                               inplace = True)

#Strip repeated text from Location and Trailhead
for i in list(range(0,df_hikes.shape[0])):
    #Clean Trailhead
    if type(df_hikes.Location[i]) == str:
        pat = df_hikes.Location[i]
        df_hikes.Trailhead[i] = df_hikes.Trailhead[i].replace(pat, '').strip()
    #Clean Location

    if type(df_hikes.Region[i]) == str:
        pat = df_hikes.Region[i] + ' -- '
        df_hikes.Location[i] = df_hikes.Location[i].replace(pat, '').strip()

df_hikes.Trailhead = df_hikes.Trailhead.str.replace('See weather forecast', '')

#Fix Boolean Variables
cols = ['Dogs_Leashed',
        'Dogs_None',
        'Kid_Friendly',
        'Campsites',
        'Lakes',
        'Rivers',
        'Mountain_Views',
        'Summits',
        'Ridges_Passes',
        'Old_Growth',
        'Fall_Foliage',
        'Flowers_Meadows',
        'Wildlife']

for col in cols:
    df_hikes[col] = np.where(df_hikes[col] == '', True, False)

#Replace NaN with empty string for text entries
cols = ['Description', 'Directions', 'Alerts', 'Permits']

for col in cols:
    df_hikes[col].fillna('', inplace = True)

#Update data types
df_hikes = df_hikes.apply(pd.to_numeric, errors='ignore')

#Update Categorical Fields
col_cat = []
for col in df_hikes.columns:
    tp = df_hikes[col].dtype == 'object'
    nu = df_hikes[col].nunique() <= 75
    if (tp & nu):
        col_cat.append(col)

#for col in col_cat:
#    print(col)
#    print(df_hikes[col].value_counts()[:6])
#    print()

df_hikes[col_cat] = df_hikes[col_cat].astype('category')

# Organize Columns
gp_core = ['ID', 'URL', 'Name']
gp_area = ['Region', 'Location','Trailhead']
gp_gps = ['Lat', 'Long']
gp_stats = ['Distance', 'Distance_Type', 'Elevation_Gain', 'Elevation_Peak']
gp_text = ['Description', 'Directions']
gp_pop = ['Rating', 'Rating_Cnt', 'Trip_Report_Cnt']
gp_feat  = ['Dogs_Leashed', 'Dogs_None', 'Kid_Friendly', 'Campsites', 'Lakes', 'Rivers', 'Mountain_Views', 'Summits', 'Ridges_Passes', 'Old_Growth', 'Fall_Foliage', 'Flowers_Meadows', 'Wildlife']
gp_other = ['Alerts', 'Permits']

df_hikes = df_hikes[gp_core + gp_area + gp_gps + gp_stats + gp_text + gp_pop + gp_feat + gp_other]

#Create summary
df_sum = pandas_summary.DataFrameSummary(df_hikes)
np.transpose(df_sum.columns_stats)

print('Complete')
# =============================================================================
#                              Export Data
# =============================================================================
print('Exporting Data...', end='')

#Save csv
df_hikes.to_csv("../Data/hikes.csv", index = False, encoding = "utf-8")
df_hikes.to_pickle("../Data/hikes.pkl")

print('Complete')
