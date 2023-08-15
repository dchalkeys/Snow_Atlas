#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
import os
import csv
import arcpy
from arcgis.gis import GIS
import arcgis
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

plt.rcParams.update({'figure.max_open_warning': 0})


#use ArcGIS Pro to automatically log into active user to void signing in through organization
gis=GIS('Pro')

for filename in os.listdir(r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\Raw_Data\Modeling\US\US_Snow_Scratch'):
    if filename.endswith('.csv'):
        with open(os.path.join(r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\Raw_Data\Modeling\US\US_Snow_Scratch', filename)) as file:
            
            df = pd.read_csv(file, parse_dates=['Date'], low_memory=False)
            
            #rename 'time stamp' field 'datetime' 
            df2 = df.rename(columns={'Date':'datetime'})
            
            for col in df2.columns:
                
                #use conditional statements to pass through all columns that are not snow depth
                if 'Change' in col:
                    pass
                
                elif 'Snow Depth' in col:
                    pass
                
                elif 'datetime' in col:
                    pass
                
                #process for snow depth columns:
                else:

                    #determine the water year
                    df2['water_year'] = df2.datetime.dt.year.where(df2.datetime.dt.month < 10, df2.datetime.dt.year + 1)

                    #add column for count of readings by water year
                    df2['count'] = df2.groupby('water_year')['water_year'].transform('count')

                    #get names of indexes for which count is less than threshold for complete years
                    incomplete_year = df2[ df2['count'] < 360 ].index

                    #delete these row indexes from dataFrame
                    df2.drop(incomplete_year , inplace=True)

                    #get names of indexes for which Value column has value greater than threshold for errors
                    over_range = df2[ df2[col] > 3000 ].index

                    #delete these row indexes from dataFrame
                    df2.drop(over_range , inplace=True)

                    #add new column for the difference between sd value and the previous value
                    df2['difference'] = df2[col].diff()

                    #create empty list for error readings
                    errors = []

                    #locate absolute value of differences greater than x
                    #if positive add sd value to errors list
                    #else negative add previous sd value to errors list
                    for i in range(1, len(df2)):
                        if abs(df2['difference'].iloc[i]) > 1000:
                            if df2['difference'].iloc[i] > 0:
                                errors.append(df2[col].iloc[i])
                            else:
                                errors.append(df2[col].iloc[i-1])
                        else:
                            pass

                    #redefine dataframe without values in error list
                    df2 = df2[~df2[col].isin(errors)]

                   #calculate max snow depth for each water year--> creates dataframe with 2 columns, water_year, snow depth
                    max_swe_wateryear_all = df2.groupby('water_year')[[col]].max()

                    #drop rows with NaN values
                    max_swe_wateryear = max_swe_wateryear_all.dropna(axis = 0, how ='any')

                    if max_swe_wateryear.shape[0] > 0:

                        partitioned_col = col.partition(' Snow Water')

                        station_name = str(partitioned_col[0])
                        
                        #use ArcGIS Pro to automatically log into active user to void signing in through organization
                        gis=GIS('Pro')
                        
                        added_items = []
                        added_items = gis.content.search(query= 'title: ' + station_name + ' Max Snow Water Equivalent')
                        if bool(added_items) == False:
                            
                            #make bar chart
                            fig = max_swe_wateryear.plot.bar(figsize=(8, 6), xlabel='Water Year', ylabel='Max Snow Water Equivalent (millimeters)', title = station_name + ' Maximum Snow Water Equivalent by Water Year', legend=False)
                            
                    

                            #create path and save figure
                            graph_path = os.path.join(r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\Raw_Data\Modeling\US\US_SnowWater_Graphs', station_name) +'_SWE.png'

                            plt.savefig(graph_path)

                            #declare graph properties
                            graph_properties={'title':station_name + ' Max Snow Water Equivalent by Water Year',
                                              'type':'Image',
                                              'tags':'snotel, telemetry, snow water equivalent, SWE, snowpack, climate change, North America'}


                            #set thumbnail as graph
                            thumbnail_path = graph_path


                            #add item
                            graph_item = gis.content.add(data = graph_path, item_properties = graph_properties, thumbnail = thumbnail_path)
                            graph_item

                            #share item
                            graph_item.share(everyone=True)

                            #declare url for item to url for item in my content with item id
                            data_URL = r"https://arcgis-content.maps.arcgis.com/sharing/rest/content/items/" + str(graph_item.id) +"/data"

                            print('Station Name: ' + station_name)
                            print('URL: ' + str(data_URL))


                            #declare feature class and fields
                            FC = r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\NorthAmerican_Snowpack.gdb\US_Snotels'
                            Fields = ['site_name', 'SWE_ImageLink']

                            #use update cursor to populate image link field with url to item page
                            with arcpy.da.UpdateCursor(FC,Fields) as ucursor:
                                for row in ucursor:
                                    if row[0] == station_name:
                                        row[1] = data_URL
                                        ucursor.updateRow(row)
                                        print('Feature image link updated.\n')
                                    else:
                                        pass
                        else:
                            pass





# In[ ]:




