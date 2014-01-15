'''This module formats a Traffic Information GeoRSS feed as provided by the UK Government for application use.

Author: Hayley Hume-Merry <hayley@thundermaps.com>
Date: 9 January 2014'''

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET

class Incidents:
    def format_feed(self):
        #Retrieves the GeoRSS feed using the urllib.request library and stores as xml
        traffic_feed = urllib.request.urlretrieve('http://hatrafficinfo.dft.gov.uk/feeds/rss/AllEvents.xml', 'incident_feed.xml')
        tree = ET.parse('incident_feed.xml')
        listings = []
        #iterates through the incidents and extracts information
        for item in tree.iter(tag='item'):
            date = item.find('pubDate').text
            format_date = self.format_datetime(date)
            #format each parameter into JSON format for application use
            listing = {"occurred_on":format_date, 
                        "latitude":item.find('latitude').text, 
                        "longitude":item.find('longitude').text, 
                        "description":item.find('description').text,
                        "category_name":item.find('category').text,
                        "source_id":item.find('reference').text}
            #create a list of dictionaries
            listings.append(listing)
        return listings
    
            
    def format_datetime(self, date):
            #convert date and time format from GMT to UTC
            date_time = date.split()
            day = date_time[1]
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            month = date_time[2]
            if month in monthDict:
                month = monthDict[month]
            year = date_time[3]
            date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[4])
            
            local = pytz.timezone("GMT")
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = str(utc_dt)
            return utc_dt
