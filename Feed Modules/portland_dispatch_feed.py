#
#dispatch_feed.py
#Module for pushing new Portland 911 Dispatch updates.
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET


class Dispatch:
    def format_feed(self):
         #Retrieves the data feed and stores it as xml
        dispatch_file = urllib.request.urlretrieve('http://www.portlandonline.com/scripts/911incidents.cfm', 'dispatch_feed.xml')
        tree = ET.parse('dispatch_feed.xml')
        listings = []
        for entry in tree.iter('{http://www.w3.org/2005/Atom}entry'):
            location = entry[6].text.split()
            latitude = location[0]        
            longitude = location[1]
            date_time = entry[5].text.replace('T', ' ')
            dispatch_id = entry[0].text
            dispatch_id = dispatch_id[-13:]
            dispatch_title = entry[4].attrib
            dispatch_title = dispatch_title['label'].title() + ' - Portland 911'
            agency = entry[3].text.replace('at', 'Location: ').split('[')
            summary = agency[0][:-5].title()
            agency = "Portland Dispatch Agency: " + agency[1][:-16]
            description = summary + '\n' + agency
            #format each parameter into a dictionary
            listing = {"occurred_on":date_time, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":dispatch_title,
                       "source_id":dispatch_id}
            #create a list of dictionaries
            listings.append(listing)
        return listings