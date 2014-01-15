#
#fire_alerts.py
#Module for formatting new New South Wales Rural Fire Alerts.
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET


class Fires:
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        dispatch_file = urllib.request.urlretrieve("http://www.rfs.nsw.gov.au/feeds/majorIncidents.xml", 'fire_alerts.xml')
        tree = ET.parse('fire_alerts.xml')
        listings = []
        for item in tree.iter(tag='item'):
            incident_name = item[0].text.title()
            incident_id = item[3].text.split(':')
            incident_id = incident_id[2]
            location = item[6].text.split()
            latitude = location[0]
            longitude = location[1]
            summary = item.find("description").text.split('<br />')
            incident_type = summary[4] + " - NSW".upper() + " Fire Incidents".title()
            date_time = summary[-1][9:]
            format_date = self.format_datetime(date_time)
            description = incident_name + ' - ' + summary[3][8:].title() + '\n' + summary[6].title() + '\n' + summary[1].title()
            #format each parameter into a dictionary
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":incident_type,
                       "source_id":incident_id}
            #create a list of dictionaries
            listings.append(listing)            
        return listings
        
    def format_datetime(self, date_time):
        #convert date and time format from EST to UTC
            date_time = date_time.split()
            day = date_time[0]
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            month = date_time[1]
            if month in monthDict:
                month = monthDict[month]
            year = date_time[2]
            date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[3])
            
            local = pytz.timezone("Australia/NSW")
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = str(utc_dt)
            return utc_dt