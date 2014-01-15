#
#mobile_library.py
#Module for pushing new Mobile Library Locations for Chirstchurch, New Zealand.
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET
from geopy import geocoders

class Library:
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        urllib.request.urlretrieve("http://www.trumba.com/calendars/Mobile.rss", 'mobile_library.xml')
        tree = ET.parse('mobile_library.xml')
        listings = []
        for item in tree.iter(tag='item'):
            summary = item[1].text.split('<br/>')
            address = summary[0]
            title_address = item[0].text.replace('.', ':').split(':')
            if title_address[0] != 'New Year':
                title_address = title_address[1].strip()
                location = self.geocoder(address, title_address)
                if location == None:
                    continue
                latitude = location[1][0]
                longitude = location[1][1]
                date_time = item[5].text
                format_date = self.format_datetime(date_time)
                unique_id = item[2].text.split('%')
                unique_id = unique_id[-1]
                title = item[0].text
                if 'Mobile ' in title:
                    start = title.index('Mobile ')
                    end = start + 8
                    mobile_title = title[start:end] + " - Christchurch Mobile Library"
                else:
                    mobile_title = "Chirstchurch Mobile Library"
                description = summary[1].replace('&nbsp;&ndash;&nbsp;', ' until ')
                description = description + '\n' + 'For more information go to: http://christchurchcitylibraries.com/mobiles/'
                #format each parameter into a dictionary
                listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":mobile_title,
                       "source_id":unique_id
                       }
                listings.append(listing)
        return listings
            
    def geocoder(self, address, title_address):
        #Geocodes addresses using the GoogleV3 package. This converts addresses to lat/long pairs
        weekdays = {1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday', 7:'Sunday'}
        checker = address.split(',')
        if checker[0] in weekdays.values():
            try:
                g = geocoders.GoogleV3()
                (lat, long) = g.geocode(title_address)
                if (lat, long) == 'None':
                    pass
                else:
                    return (lat, long)
            except TypeError:
                pass
        else:
            try:
                g = geocoders.GoogleV3()
                (lat, long) = g.geocode(address)
                if (lat, long) == 'None':   
                    pass
                else:
                    return (lat, long)
            except TypeError:
                pass 
           
            
    def format_datetime(self, date_time):
        #convert date and time format from GMT to UTC
                date_time = date_time.replace(' GMT', '').split()
                day = date_time[0]
                monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                month = date_time[1]
                if month in monthDict:
                    month = monthDict[month]
                year = date_time[2]
                date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[3])
                
                local = pytz.timezone("GMT")
                naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                local_dt = local.localize(naive, is_dst = None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = str(utc_dt)
                return utc_dt