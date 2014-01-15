#
#imagery.py
#Module for pushing new Lansat 7 Satellite updates.
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET


class Imagery:
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        image_file = urllib.request.urlretrieve("http://landsat.usgs.gov/Landsat7.rss", 'landsat_feed.xml')
        tree = ET.parse('landsat_feed.xml')     
        listings = []
        for item in tree.iter(tag='item'):
            imagery_name = item[0].text.split()
            imagery_name = imagery_name[0] + ' ' + imagery_name[1] + ' ' + imagery_name[2] + ' ' + imagery_name[3]
            summary = item[2].text.split('\n')
            imagery_id = summary[-2][10:]
            path_row = summary[5].split(',')
            #image_link = summary[2].split()
            #image_link = image_link[0] + ' ' + image_link[1] + ' ' + 'alt="Landsat7" </img>' 
            imagery_position = path_row[0] + ' -' + path_row[1] + " - Satellite Image"
            description = summary[4][:19] + '\n' + imagery_id + '\n' + imagery_position + '\n' + path_row[2][1:-5] #+ '\n' + image_link
            date_time = item[0].text
            format_date = self.format_datetime(date_time)
            latitude = item[4].text
            longitude = item[5].text
            #format each parameter into a dictionary
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":imagery_position,
                       "source_id":imagery_id}
            #create a list of dictionaries
            listings.append(listing)
        return listings
            
    def format_datetime(self, date_time):
        #convert date and time format from GMT to UTC
            date_time = date_time.replace(' GMT', '').split()
            date_time = date_time[4] + ' ' + date_time[6]
            
            local = pytz.timezone("GMT")
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = str(utc_dt)
            return utc_dt