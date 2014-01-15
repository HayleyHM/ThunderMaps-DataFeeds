#
#earthquakes.py
#Module for pushing new UK Earthquake updates.
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import time
import xml.etree.ElementTree as ET


class Quakes:
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        quake_file = urllib.request.urlretrieve("http://www.bgs.ac.uk/feeds/MhSeismology.xml", 'quake_alerts.xml')
        tree = ET.parse('quake_alerts.xml')
        listings = []
        for item in tree.iter(tag='item'):
            incident_name = item[0].text.split(':')
            incident_name = incident_name[0] + '- ' + incident_name[2].title()
            summary = item[1].text.split(';')
            incident_id = summary[2][11:-2].replace(',', '').replace('.', '').replace('-', '')
            latitude = item[5].text
            longitude = item[6].text
            date_time = summary[0][23:-5]
            format_date = self.format_datetime(date_time)
            description = summary[1][1:].title() + '\n' + summary[0] + '\n' + summary[3][1:] + '\n' + summary[4][1:]
            #format each parameter into a dictionary
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":incident_name,
                       "source_id":incident_id}
            #create a list of dictionaries
            listings.append(listing)            
        return listings
        
    def format_datetime(self, date_time):
        #convert date and time format to UTC
                date_time = date_time.split()
                day = date_time[0]
                monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                month = date_time[1]
                if month in monthDict:
                    month = monthDict[month]
                year = '20' + date_time[2]
                date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[3])
                
                return date_time