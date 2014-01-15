#
#global_alerts.py
#Module for pushing Global Alert updates from Global Disaster Alert and Coordinate System website. <http://www.gdacs.org/>
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import time
import pytz, datetime
import xml.etree.ElementTree as ET


class Incidents:
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        demolitions_file = urllib.request.urlretrieve('http://www.gdacs.org/XML/RSS.xml', 'global_incidents.xml')
        tree = ET.parse('global_incidents.xml')
        listings = []
        for item in tree.iter(tag='item'):
            alert_title = item[0].text
            latitude = item[9][0].text
            longitude = item[9][1].text
            description = alert_title + ' - ' + '\n' + item[1].text
            unique_id = item[3].text.split('=')
            unique_id = unique_id[-1]
            incident_type = item[12].text
            event_type = self.incident(incident_type) + " - Global Disaster Alert"
            date_time = item[4].text
            format_date = self.format_datetime(date_time)
            #format each parameter into a dictionary
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":event_type,
                       "source_id":unique_id}
            #create a list of dictionaries
            listings.append(listing)            
        return listings
    
    
    def incident(self, incident_type):
        #Redefine the event incident type for users
        event = {'FL':'Flood', 'EQ':'Earthquake', 'TC':'Tropical Cyclone'}
        if incident_type in event.keys():
            event_type = event[incident_type]
        else:
            event_type = "Incident Alert"
            
        return event_type
            
    def format_datetime(self, date_time):
        #convert date and time format from GMT to UTC
            date_time = date_time.strip(' GMT').split()
            day = date_time[1]
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            month = date_time[2]
            if month in monthDict:
                month = monthDict[month]
            year = date_time[3]
            date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + date_time[4]
    
            local = pytz.timezone("GMT")
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = str(utc_dt)
            return utc_dt