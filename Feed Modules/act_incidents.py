#
#incidents.py
#Module for pushing new Australian Captial Territory Incident updates through to users
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET


class Incidents:    
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        incidents = urllib.request.urlretrieve('http://esa.act.gov.au/feeds/currentincidents.xml', 'incident_feed.xml')
        tree = ET.parse('incident_feed.xml')
        listings = []
        for item in tree.iter(tag='item'):
            incident_name = item[0].text
            unique_id = item[3].text
            date_time = item[4].text
            date = self.format_datetime(date_time)
            location = item[5].text
            location = location.split()
            latitude = location[0]
            longitude = location[1]
            description = item[2].text
            description = description.split('<br />')
            incident_id = description[-3].replace('Incident Number: ', '')
            incident_type = description[4].replace('Type: ', '') + ' - ACT Government'
            call_time = description[-1].strip('\n')
            agency = "Response " + description[5]
            description = incident_name.title() + '\n' + call_time + '\n' + agency
            #format each parameter into a dictionary
            listing = {"occurred_on":date, 
                        "latitude":latitude, 
                        "longitude":longitude, 
                        "description":description,
                        "category_name":incident_type,
                        "source_id":incident_id}
            #create a list of dictionaries
            listings.append(listing)            
        return listings
                
           
    def format_datetime(self, date_time):
        #convert date and time format from AEST to UTC
        date_time = date_time.strip('EST').split()
        day = date_time[0]
        monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        month = date_time[1]
        if month in monthDict:
            month = monthDict[month]
        year = date_time[2]
        date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[3])
        
        local = pytz.timezone("Australia/Victoria")
        naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst = None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = str(utc_dt)
        return utc_dt