'''This module can be used to retrieve live Queensland, Australia Fire Service Data.

Author: Hayley Hume-Merry <hayley@thundermaps.com>
Date: 23 December 2013'''

import urllib.request
import time
import xml.etree.ElementTree as ET
import pytz, datetime

class Fires():
    def format_feed(self):
        #Retrieves and formats the piracy data from NATO's RSS Feed
        feed_file = urllib.request.urlretrieve('https://ruralfire.qld.gov.au/bushfirealert/bushfireAlert.xml', 'qld_fires.xml')
        tree = ET.parse('qld_fires.xml')
        listings = []
        for alert in tree.iter(tag='item'):
            #Extracts the data from a number of subheadings within the feed
            summary = alert.find('description').text.split('<br />')
            title = summary[0].split(':')
            title = title[1][:-1]
            description = summary[4] + ' ' + summary[3]
            location = alert[6].text.split()
            latitude = location[0]
            longitude = location[1]
            fire_id = alert.find('title').text
            date = alert.find('pubDate').text
            format_date = self.format_datetime(date)
            #Converts the data into JSON format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":title + 'QLD Fire Incidents',
                       "source_id":fire_id
                }
            listings.append(listing)
        return listings        
    
    def format_datetime(self, date):
            #Re-formats the publish time/date into UTC format
                date_time = date.split()
                day = date_time[1]
                monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                month = date_time[2]
                if month in monthDict:
                    month = monthDict[month]
                year = date_time[3]
                date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[4])
                
                local = pytz.timezone("Australia/Queensland")
                naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                local_dt = local.localize(naive, is_dst = None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = str(utc_dt)
                return utc_dt        