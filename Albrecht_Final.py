
#********************************************************************************************************************
# Name:              Final Script
# Created:           03/17/21
# Author:            Dylan Albrecht
# Description:       Iterates through folder of files of snow depth readings, creates graph of maximum snow depth by
#                    water year for each file, uploads graph to arcgis online content, and populates field in snotel station feature
#                    class with link to graph for each snotel station.
#*********************************************************************************************************************
# import modules for time stamp and error catcher
import datetime

# import module for arcpy
import arcpy

# Current time stamp
RightNow = datetime.datetime.now()





#***********************************************************************
# section title
#***********************************************************************
RightNow = datetime.datetime.now()

#remember this verbose error catcher.  Error messaging makes it invaluable.
try:
  #Your variables, environment settings, and entire script go into the
  #try statement for error testing.  If an error is found you drop to the
  #except statement and are given a complete error message.

  import pandas as pd
  import os
  import csv
  import arcpy
  from arcgis.gis import GIS
  import arcgis


  #iterate through fold of snow depth tables
  for filename in os.listdir(r'C:\Users\dchal\ENVS423\Final\Data\BCtry'):
      if filename.endswith('.csv'):
          with open(os.path.join(r'C:\Users\dchal\ENVS423\Final\Data\BCtry', filename)) as file:
              
              #define data frame as file with no memory limits and dates parsed by 'time stamp' field
              df = pd.read_csv(file, parse_dates=['Timestamp (UTC)'], low_memory=False)

              #display header
              df.head()

              #rename 'time stamp' field 'datetime' 
              df = df.rename(columns={'Timestamp (UTC)':'datetime'})

              #drop na values
              df = df.dropna()

              #get names of indexes for which Value column has value greater than 350 centimeters
              over_range = df[ df['Value (Centimetres)'] > 350 ].index

              #delete these row indexes from dataFrame
              df.drop(over_range , inplace=True)

              #determine the water year
              df['water_year'] = df.datetime.dt.year.where(df.datetime.dt.month < 10, df.datetime.dt.year + 1)

              #calculate max snow depth for each water year
              annual_max_snow_depth = df.groupby('water_year')[['Value (Centimetres)']].max()

              #make bar chart
              fig = annual_max_snow_depth.plot.bar(figsize=(8, 6), xlabel='Water Year', ylabel='Max Snow Depth (centimeters)', legend=False)

              #create path and save figure
              graph_path = os.path.join(r'C:\Users\dchal\ENVS423\Final\Data\BCtry', filename[0:5])+'.png'
              plt.savefig(graph_path)


              #use ArcGIS Pro to automatically log into active user to void signing in through organization
              gis=GIS('Pro')

              #declare graph properties
              graph_properties={'title':filename[0:5],
                                'type':'Image',
                                'tags':'arcgis, python, snow depth, climate change, cascadia'}
             

              #set thumbnail as graph
              thumbnail_path = graph_path


              #add item
              graph_item = gis.content.add(data = graph_path, item_properties = graph_properties, thumbnail = thumbnail_path)
              graph_item

              #share item
              graph_item.share(org=True)

              #declare url for item to url for item in my content with item id
              URL = r"https://wwu.maps.arcgis.com/home/item.html?id=" + str(graph_item.id)
              
              print(graph_item)
              print(str(graph_item.title)+" url:"+URL)
              
              #declare feature class and fields
              FC = r'C:\Users\dchal\ENVS421\Final\Final.gdb\CAS_CAN_Snotel_proj'
              Fields = ['LOCATION_ID', 'Image_link']
      
              #use update cursor to populate image link field with url to item page
              with arcpy.da.UpdateCursor(FC,Fields) as ucursor:
                  for row in ucursor:
                      if row[0] == filename[0:5]:
                          arcpy.management.CalculateField(FC, 'Image_link', "URL")
                      else:
                          pass

except:
#imported modules produce error messaging from both ArcPy and Python.
  import string, os, sys, traceback #if needed
  # Get the traceback object
  tb = sys.exc_info()[2]
  tbinfo = traceback.format_tb(tb)[0]
  # Concatenate information together concerning the error into a message string
  pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
  msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
  # Return python error messages for use in script tool or Python Window
  arcpy.AddError(pymsg)
  arcpy.AddError(msgs)
  # Print Python error messages for use in Python / Python Window
  print (pymsg + "\n")
  print (msgs)

#***********************************************************************
# Time Finish up
#***********************************************************************
endtime = datetime.datetime.now()
elapsed = endtime - RightNow  # this is a timedelta object in days and seconds
days, seconds = elapsed.days, elapsed.seconds
hours = seconds // 3600
minutes = (seconds % 3600) // 60
seconds = seconds % 60
print ("\nThat took {} days, {} hours, {} minutes, {} seconds".format(days, hours, minutes, seconds))
#***********************************************************************


print ('\n\n--> Finished Script... ')
