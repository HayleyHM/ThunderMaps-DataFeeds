"""This module uses a Fire 911 Dispatch - GeoRSS feed from the Columbia City Government to format the data for application use. The data is updated every 60 seconds.

Author: Hayley Hume-Merry <hayley@thundermaps.com>
Date: 09 January 2014"""

import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET


class Dispatch:
    def format_feed(self):
        #Uses the urllib.request library to import the GeoRSS feed and saves as xml
        incident_feed = urllib.request.urlretrieve('http://www.gocolumbiamo.com/PSJC/Services/911/911dispatch/fire_georss.php/eqcenter/catalogs/rssxsl.php?feed=eqs7day-M5.xml', 'Columbia_fire.xml')
        tree = ET.parse('Columbia_fire.xml')
        listings = []
        #Iterates through each incident in the feed and extracts useful information
        for item in tree.iter(tag='item'):
            #formats each parameter into a JSON format for application use
            date = item.find('pubDate').text
            format_date = self.format_datetime(date)
            listing = {"occurred_on":format_date, 
                        "latitude":item.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}lat').text, 
                        "longitude":item.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}long').text, 
                        "description": item.find('description').text,
                        "category_name": item.find('title').text.title() + ' - Columbia Fire Dispatch',
                        "source_id":item.find('.//{http://www.gocolumbiamo.com/PSJC/Services/911/911dispatch/calldatachema.php#}InNum').text}
            #create a list of dictionaries
            listings.append(listing)
        return listings        
    
    def format_datetime(self, date):
        #convert date and time format from CST to UTC
        date_time = date.split()
        day = date_time[1]
        monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        month = date_time[2]
        if month in monthDict:
            month = monthDict[month]
        year = date_time[3]
        date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[4])
        
        local = pytz.timezone("CST6CDT")
        naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst = None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = str(utc_dt)
        return utc_dt