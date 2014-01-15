#
#inciweb.py
#Module for pushing new InciWeb Incidents from the Incident Information System site. <http://inciweb.org/>
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import time
import pytz, datetime
import xml.etree.ElementTree as ET


class Incidents:
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        demolitions_file = urllib.request.urlretrieve('http://inciweb.nwcg.gov/feeds/rss/incidents/', 'inciweb_feed.xml')
        tree = ET.parse('inciweb_feed.xml')
        listings = []
        for item in tree.iter(tag='item'):
            incident = item[0].text
            incident = incident.split('(')
            incident_title = incident[0].strip()
            incident_type = incident[1].strip(')') + " - Inciweb Incident"
            latitude = item[4].text
            longitude = item[5].text
            unique_id = item[6].text.split('/')
            unique_id = unique_id[-2]
            description = incident_title + ' - ' + item[-1].text
            date_time = item[1].text
            format_date = self.format_datetime(date_time)
            #format each parameter into a dictionary
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":incident_type,
                       "source_id":unique_id}
            #create a list of dictionaries
            listings.append(listing)            
        return listings
            
    def format_datetime(self, date_time):
        #convert date and time format to UTC
        date_time = date_time.split()
        day = date_time[1]
        monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        month = date_time[2]
        if month in monthDict:
            month = monthDict[month]
        year = date_time[3]
        date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + date_time[4] + date_time[5]
        
        return date_time