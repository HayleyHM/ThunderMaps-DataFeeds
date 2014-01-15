'''This module can be used to retrieve and format Worldwide Earthquakes as provided by the BGS School Seismology Project

Author: Hayley Hume-Merry
Date: 07 January 2014'''

import urllib.request
import time
import pytz, datetime
import xml.etree.ElementTree as ET

class Quakes:
    def format_feed(self):
        #Retrieves the quake data from the BGS website
        quakes_file = urllib.request.urlretrieve('http://www.bgs.ac.uk/feeds/SchoolSeismology.xml', 'world_quakes.xml')
        tree = ET.parse('world_quakes.xml')
        listings = []
        for item in tree.iter(tag='item'):
            #Formats the xml data into relevant subheadings
            date = item.find('pubDate').text
            format_date = self.format_datetime(date)
            category = item.find('title').text.split(', ')
            category_place = 'Earthquake - ' + category[2].title()
            quake_id = item.find('link').text.split('quake_id=')
            #Converts the data into JSON format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":item[5].text, 
                       "longitude":item[6].text, 
                       "description":item.find('description').text,
                       "category_name":category_place,
                       "source_id":quake_id[1],
                }
            listings.append(listing)
        return listings        
         
            
    def format_datetime(self, date):
        #Converts the date and time from GMT to UTC format
            date_time = date.split()
            day = date_time[1]
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            month = date_time[2]
            if month in monthDict:
                month = monthDict[month]
            year = date_time[3]
            time = date_time[4]
            format_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(time)
           
            local = pytz.timezone("GMT")
            naive = datetime.datetime.strptime(format_time, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = str(utc_dt)
            return utc_dt