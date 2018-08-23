# -*- coding: utf-8 -*-
"""
WTA Report Cleaning
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
import pandas_summary

# =============================================================================
#                                 Import Data
# =============================================================================

# Import Hike Data (Molten State)
df_rpts_molten = pd.read_csv('../Data/reports_data_molten.csv', encoding = "utf-8", engine = 'python')


# =============================================================================
#                                Basic Cleaning
# =============================================================================

# Remove Incomplete Records
df_rpts_molten.dropna(inplace=True)

# Remove Duplicates
df_rpts_molten.drop_duplicates(subset = ['ID', 'Key'], inplace=True)

# Pivot Data to tidy/wide format
df_rpts = df_rpts_molten.pivot(index = 'ID', columns = 'Key', values = 'Value')
df_rpts.reset_index(inplace=True)
del df_rpts_molten

#Remove reports that are missing a hike ID
df_rpts = df_rpts[df_rpts.HikeID.notna()]

#Rename ID field as "ReportID"
df_rpts.rename(columns = {'ID':'ReportID'}, inplace=True)

# =============================================================================
#                              Clean Variables
# =============================================================================

# Trail Conditions
# Split basic condition category from list of hazards
df_tc = df_rpts.Cond_TrailConditions.str.split(':', expand=True)
df_rpts['Cond_Trail'] = df_tc[0]
df_rpts.rename(columns = {'Cond_TypeofHike':'TypeofHike'}, inplace=True)
del df_tc[0]

# Convert hazards into list of dummy variables
df_tc = df_tc[1].str.strip()
df_tc = df_tc.str.replace('.', '')
df_tc = df_tc.str.replace(' ', '')
df_tc = df_tc.str.replace('/', '')
df_tc = df_tc.str.replace('(', '')
df_tc = df_tc.str.replace(')', '')
df_tc = df_tc.str.get_dummies(',    ')

rename = {'Bridgeout':'Haz_BridgeOut',
          'Difficultstreamcrossings':'Haz_DifStreamCrossing',
          'MudRockslideorwashout':'Haz_Washout',
          'Muddyorwettrail':'Haz_Muddy',
          'Overgrowninplaces':'Haz_Overgrown',
          'Treesdownacrosstrail':'Haz_DownTrees'
          }

df_tc.rename(columns = rename, inplace=True)
df_rpts = pd.concat([df_rpts, df_tc], axis=1)
del df_tc
del rename
df_rpts.drop(columns = 'Cond_TrailConditions', inplace=True)

#Quantify Trip Conditions - Based on occurence
col_conds = df_rpts.columns[df_rpts.columns.str.startswith('Cond')]
for col in col_conds:
    print('\n',col)
    print(df_rpts[col].value_counts()/df_rpts[col].value_counts().max())
    levs = df_rpts[col].value_counts()/df_rpts[col].value_counts().max()
    for i in list(range(levs.shape[0])):
        df_rpts[col] = np.where(df_rpts[col] == levs.index[i], levs[i], df_rpts[col])

#Fix Feature Boolean Variables
col_feats = df_rpts.columns[df_rpts.columns.str.startswith('Feat')]
for col in col_feats:
    df_rpts[col] = np.where(df_rpts[col] == 'True', True, False)

#Fix Hazard Boolean Variables
col_haz = df_rpts.columns[df_rpts.columns.str.startswith('Haz')]
for col in col_haz:
    df_rpts[col] = np.where(df_rpts[col] == 1, True, False)


#Replace NaN with empty string for text entries
df_rpts['ReportBody'].fillna('', inplace = True)

#Update data types
df_rpts = df_rpts.apply(pd.to_numeric, errors='ignore')

#Update Categorical Fields
col_cat = []
for col in df_rpts.columns:
    tp = df_rpts[col].dtype == 'object'
    nu = df_rpts[col].nunique() <= 25
    if (tp & nu):
        col_cat.append(col)

for col in col_cat:
    print(col)
    print(df_rpts[col].value_counts()[:6])
    print()

df_rpts[col_cat] = df_rpts[col_cat].astype('category')

# Organize Columns
gp_core = ['ID', 'URL', 'Name']
gp_area = ['Region', 'Location','Trailhead']
gp_gps = ['Lat', 'Long']
gp_stats = ['Distance', 'Distance_Type', 'Elevation_Gain', 'Elevation_Peak']
gp_text = ['Description', 'Directions']
gp_pop = ['Rating', 'Rating_Cnt', 'Trip_Report_Cnt']
gp_feat  = ['Dogs_Leashed', 'Dogs_None', 'Kid_Friendly', 'Campsites', 'Lakes', 'Rivers', 'Mountain_Views', 'Summits', 'Ridges_Passes', 'Old_Growth', 'Fall_Foliage', 'Flowers_Meadows', 'Wildlife']
gp_other = ['Alerts', 'Permits']



#########################################################################
#########################################################################
#########################################################################
#########################################################################



df_rpts = df_rpts[gp_core + gp_area + gp_gps + gp_stats + gp_text + gp_pop + gp_feat + gp_other]

#Create summary
df_sum = pandas_summary.DataFrameSummary(df_rpts)
np.transpose(df_sum.columns_stats)

#Save csv
df_rpts.to_csv("../Data/reports.csv", index = False, encoding = "utf-8")
df_rpts.to_pickle("../Data/reports.pkl")
