'''This module can be used to retrieve live NATO Piracy Data

Author: Hayley Hume-Merry <hayley@thundermaps.com>
Date: 23 December 2013'''

import urllib.request
import time
import xml.etree.ElementTree as ET
import pytz, datetime

class Piracy:
    def format_feed(self):
        #Retrieves and formats the piracy data from NATO's RSS Feed
        feed_file = urllib.request.urlretrieve("http://www.shipping.nato.int/_layouts/listfeed.aspx?List=77c1e451-15fc-49db-a84e-1e8536ccc972&View=721a920c-538a-404e-838b-30635159e886", "piracy_feed.xml")
        tree = ET.parse("piracy_feed.xml")
        listings = []
        for alert in tree.iter(tag='item'):
            summary = alert.find('description').text.split('<div>')
            for i in summary:
                #Extracts the data from a number of subheadings within the feed
                if i.startswith('<b>Category:</b>'):
                    title = i.replace('<b>Category:</b>', '').replace('</div>', '').strip()
                    title = title + " - NATO Piracy Alerts"
                if i.startswith('<b>Latitude:</b>'):
                    latitude = i.replace('<b>Latitude:</b>', '').replace('</div>', '').strip()
                if i.startswith('<b>Longitude:</b>'):
                    longitude = i.replace('<b>Longitude:</b>', '').replace('</div>', '').strip()
                if i.startswith('<b>Details:</b>'):
                    description = i.replace('<b>Details:</b>', '').replace('</div>', '').replace('\n', '').strip()
            date = alert.find('pubDate').text
            format_date = self.format_datetime(date)
            alert_id = alert.find('guid').text.split('=')
            alert_id = alert_id[1]
            #Converts the data into JSON format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":title,
                       "source_id":alert_id
                }
            listings.append(listing)
        return listings
             
            
    def format_datetime(self, date):
        #Re-formats the publish time/date into UTC format
            date_time = date.replace(' GMT', '').split()
            day = date_time[1]
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            month = date_time[2]
            if month in monthDict:
                month = monthDict[month]
            year = date_time[3]
            date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[4])
            
            local = pytz.timezone("GMT")
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = str(utc_dt)
            return utc_dt