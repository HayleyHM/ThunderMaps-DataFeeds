"""This module uses a Current Traffic Incident - GeoRSS feed from the Tennessee Department of Transportation to format the data for application use.

Author: Hayley Hume-Merry <hayley@thundermaps.com>
Date: 09 January 2014"""

import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET

class Incidents:
    def format_feed(self):
        #Uses the urllib.request library to import the GeoRSS feed and saves as xml
        incident_feed = urllib.request.urlretrieve('http://ww2.tdot.state.tn.us/tsw/GeoRSS/TDOTIncidentGeoRSS.xml', 'tennessee_incidents.xml')
        tree = ET.parse('tennessee_incidents.xml')
        listings = []
        #Scans through each incident in the feed and extracts useful information
        for item in tree.iter(tag='item'):
            title = item.find('title').text.replace(' [', '- ').split('- ')
            date = item.find('.//{http://www.tdot.state.tn.us/tdotsmartway/}IncidentStart').text
            format_date = self.format_datetime(date)
            location = item.find('.//{http://www.opengis.net/gml}pos').text.split()
            #formats each parameter into a JSON format for application use
            listing = {"occurred_on":format_date, 
                        "latitude":location[0], 
                        "longitude":location[1], 
                        "description":item.find('description').text,
                        "category_name":title[1],
                        "source_id":item.find('guid').text}
            #create a list of dictionaries
            listings.append(listing)
        return listings
    
    def format_datetime(self, date):
                #convert date and time format from CST to UTC
                date_time = date.replace('/', ' ').split()
                day = date_time[1]
                monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                month = date_time[0]
                if month in monthDict:
                    month = monthDict[month]
                year = date_time[2]
                date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[3])
                
                local = pytz.timezone("CST6CDT")
                naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                local_dt = local.localize(naive, is_dst = None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = str(utc_dt)
                return utc_dt