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
            incident_id = item[3].text.split(':')
            location = item[6].text.split()
            summary = item.find("description").text.split('<br />')
            date_time = summary[-1][9:]
            format_date = self.format_datetime(date_time)
            #format each parameter into a dictionary
            listing = {"occurred_on":format_date, 
                       "latitude":location[0], 
                       "longitude":location[1], 
                       "description":item[0].text.title() + ' - ' + summary[3][8:].title() + '<br/>' + summary[6].title() + '<br/>' + summary[1].title(),
                       "category_name":summary[4] + " - NSW".upper() + " Fire Incidents".title(),
                       "source_id":incident_id[2]}
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