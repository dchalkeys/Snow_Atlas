#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import os
import csv
import arcpy
from arcgis.gis import GIS
import arcgis
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

plt.rcParams.update({'figure.max_open_warning': 0})

def removeElements(errors, k):
    counted = Counter(errors)
    return [el for el in errors if counted[el] >= k]

#iterate through folder of telemetry csv data, select SD telemetry csv files and open them
for filename in os.listdir(r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\Raw_Data\Modeling\Canada\CAN_Snow_Scratch'):
    if filename.endswith('.csv') and filename[14:26] == 'SW.Telemetry':
         with open(os.path.join(r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\Raw_Data\Modeling\Canada\CAN_Snow_Scratch', filename)) as file:     
                
                #define data frame as file with no memory limits and dates parsed by 'time stamp' field
            
                #declare dataframe to csv and select date field. Void low memory limits
                df = pd.read_csv(file, parse_dates=['Timestamp (UTC)'], header=2,low_memory=False)
                
                if len(df) > 10000:

                    #rename 'time stamp' field 'datetime' 
                    df = df.rename(columns={'Timestamp (UTC)':'datetime'})

                    #determine the water year
                    df['water_year'] = df.datetime.dt.year.where(df.datetime.dt.month < 10, df.datetime.dt.year + 1)

                    #add column for count of readings by water year
                    df['count'] = df.groupby('water_year')['water_year'].transform('count')

                    #get names of indexes for which count is less than threshold for complete years
                    incomplete_year = df[ df['count'] < 5000 ].index

                    #delete these row indexes from dataFrame
                    df.drop(incomplete_year , inplace=True)

                    #get names of indexes for which Value column has value greater than threshold for errors
                    over_range = df[ df['Value (Millimetres)'] > 3000 ].index

                    #delete these row indexes from dataFrame
                    df.drop(over_range , inplace=True)
                    
                    #get names of indexes for which Value column has value greater than threshold for errors
                    under_range = df[ df['Value (Millimetres)'] < 0 ].index

                    #delete these row indexes from dataFrame
                    df.drop(under_range , inplace=True)
                    
                    #add new column for the difference between sd value and the previous value
                    df['difference'] = df['Value (Millimetres)'].diff()
                    
                    #create empty list for error readings
                    errors = []
                    
                    #locate absolute value of differences greater than x,if positive add sd value to list
                    #if negative add previous sd value to list
                    for i in range(1, len(df)):
                        if abs(df['difference'].iloc[i]) > 1000:
                            if df['difference'].iloc[i] > 0:
                                errors.append(df['Value (Millimetres)'].iloc[i])
                            else:
                                errors.append(df['Value (Millimetres)'].iloc[i-1])
                        else:
                            pass
                   

                    errors = removeElements(errors, 1)
                    
                    #hi_errors = [i for i in errors if i >= 300]
                    
                    error = []
                        
                    
                    [error.append(x) for x in errors if x not in error]
                    
                    
                    error.sort()
                                     
                    #redefine dataframe without values in error list
                    df = df[~df['Value (Millimetres)'].isin(error)]
                    
                    #get names of indexes for which Value column has value greater than threshold for errors
                    under_range = df[ df['Value (Millimetres)'] < 25 ].index

                    #delete these row indexes from dataFrame
                    df.drop(under_range , inplace=True)
                    
                    df.dropna()
                    
                    #calculate max snow depth for each water year
                    annual_max_swe = df.groupby('water_year')[['Value (Millimetres)']].max()
                    
                    #drop rows with NaN values
                    annual_swe = annual_max_swe.dropna(axis = 0, how ='any')

                    if annual_max_swe.shape[0] > 0:

                        station_id = filename[27:32]
                        
                         #use ArcGIS Pro to automatically log into active user to void signing in through organization
                        gis=GIS('Pro')         

                        added_items = []
                        added_items = gis.content.search(query=filename[27:32] + " Max Snow Water Equivalent by Water Year")
                        if bool(added_items) == False:

                            #use ArcGIS Pro to automatically log into active user to void signing in through organization
                            gis=GIS('Pro')         

                            #make bar chart
                            fig = annual_max_swe.plot.bar(figsize=(8, 6), xlabel='Water Year', ylabel='Max Water Equivalent (millimeters)', title = 'B.C. Station ID: ' + filename[27:32] + ' Max Snow Water Equivalent by Water Year', legend=False)

                            #create path and save figure
                            graph_path = os.path.join(r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\Raw_Data\Modeling\Canada\CAN_SW_Graphs', filename[27:32])+'_SW.png'
                            plt.savefig(graph_path)


                            #use ArcGIS Pro to automatically log into active user to void signing in through organization
                            gis=GIS('Pro')

                            #declare graph properties
                            graph_properties={'title':'B.C. Station ID: ' + filename[27:32] + " Max Snow Water Equivalent by Water Year",
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


                            print('Station ID: ' + station_id)
                            print('URL: ' + str(data_URL))


                            #declare feature class and fields
                            FC = r'C:\Users\dchal\ENVS422\NorthAmerican_Snowpack\NorthAmerican_Snowpack.gdb\CAN_Snotels'
                            Fields = ['LOCATION_ID', 'SWE_ImageLink']

                            #use update cursor to populate image link field with url to item page
                            with arcpy.da.UpdateCursor(FC,Fields) as ucursor:
                                for row in ucursor:
                                    if row[0][0:5] == station_id:
                                        row[1] = data_URL
                                        ucursor.updateRow(row)
                                        print('Feature image link updated.\n')
                                    else:
                                        pass






# In[ ]:




