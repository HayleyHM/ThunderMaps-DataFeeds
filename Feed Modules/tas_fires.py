"""This module uses Fire Service - GeoRSS feed from the Tasmania Government to format the data for application use.

Author: Hayley Hume-Merry <hayley@thundermaps.com>
Date: 09 January 2014"""

import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET

class Incidents:
    def format_feed(self):
        #Uses the urllib.request library to import the GeoRSS feed and saves as xml
        incident_feed = urllib.request.urlretrieve('http://www.fire.tas.gov.au/Show?pageId=colBushfireSummariesRss', 'TAS_fires.xml')
        tree = ET.parse('TAS_fires.xml')
        listings = []
        #Scans through each incident in the feed and extracts useful information
        for item in tree.iter(tag='item'):
            description = item.find('description').text.strip().split('<br />')
            fire_type = description[4].split(': ')
            date = item.find('pubDate').text
            format_date = self.format_datetime(date)
            location = item.find('.//{http://www.georss.org/georss}point').text.split()
            #formats each parameter into a JSON format for application use
            listing = {"occurred_on":format_date, 
                        "latitude":location[0], 
                        "longitude":location[1], 
                        "description":description[2].strip().title() + description[3] + description[5] + description[6],
                        "category_name": fire_type[1],
                        "source_id":item.find('guid').text}
            #create a list of dictionaries
            listings.append(listing)
        return listings
    
    def format_datetime(self, date):
                    #convert date and time format from Australia/Tasmania to UTC
                    date_time = date.split()
                    day = date_time[1]
                    monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                    month = date_time[2]
                    if month in monthDict:
                        month = monthDict[month]
                    year = date_time[3]
                    date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[4])
                    
                    local = pytz.timezone("Australia/Tasmania")
                    naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                    local_dt = local.localize(naive, is_dst = None)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    utc_dt = str(utc_dt)
                    return utc_dt