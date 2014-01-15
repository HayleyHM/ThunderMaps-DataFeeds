'''This module can be used to retrieve and format Caribbean Sea Bulletins.

Author: Hayley Hume-Merry
Date: 07 January 2014'''

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET

class Caribbean:
    def format_feed(self):
        #Retrieves the RSS feed from the Pacific Region Headquarters site
        warning_file = urllib.request.urlretrieve('http://www.prh.noaa.gov/ptwc/feeds/ptwc_rss_caribe.xml', 'warning_feed.xml')
        tree = ET.parse('warning_feed.xml')
        listings = []
        for entry in tree.iter(tag='item'):
            #Formats the incident information into relevant subheadings
            title = entry.find('title').text + ': Caribbean Sea Alert'
            date = entry.find('pubDate').text
            format_date = self.format_datetime(date)
            latitude = entry[7].text
            longitude = entry[8].text
            description = entry.find('description').text.title()
            description = description.replace('<Pre>', '').replace('</Pre>', '').strip()
            entry_id = entry[3].text
            #Converts the data into JSON format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":title,
                       "source_id":entry_id,
                }
            listings.append(listing)
        return listings
    
            
    def format_datetime(self, date):
        #convert date and time format to UTC
        date_time = date.split()
        day = date_time[0]
        monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        month = date_time[1]
        if month in monthDict:
            month = monthDict[month]
        year = date_time[2]
        time = date_time[3] + date_time[4]
        format_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(time)
        return format_time