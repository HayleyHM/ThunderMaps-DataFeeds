'''This module can be used to retrieve live NATO Piracy Data and update this for users of ThunderMaps.com

Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
Date: 23 December 2013'''

import urllib.request
import time
import xml.etree.ElementTree as ET
import pytz, datetime
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'
account_id = 'nato-global-piracy-alerts'

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
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            if date_time[2] in monthDict:
                month = monthDict[date_time[2]]
            date_time = str(date_time[3]) + '-' + str(month) + '-' + str(date_time[1]) + ' ' + str(date_time[4])
            
            local = pytz.timezone("GMT")
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = str(local_dt.astimezone(pytz.utc))
            return utc_dt
        
class Updater:
    def __init__(self, key, account_id):
        self.tm_obj = Wthundermaps.ThunderMaps(key)
        self.feed_obj = Incidents()
        self.account_id = account_id
        
    def start(self):
        # Try to load the source_ids already posted.
        source_ids = []
        try:
            source_ids_file = open(".source_ids_sample", "r")
            source_ids = [i.strip() for i in source_ids_file.readlines()]
            source_ids_file.close()
        except Exception as e:
            print("! WARNING: No valid cache file was found. This may cause duplicate reports.")

        # Run until interrupt received.
        while True:
            # Load the data from the data feed.
            # This method should return a list of dicts.
            items = self.feed_obj.format_feed()
            # Create reports for the listings.
            reports = []
            for report in items:
                # Add the report to the list of reports if it hasn't already been posted.
                if report["source_id"] not in source_ids:
                    reports.append(report)
                    print("Adding %s" % report["occurred_on"])
                    # Add the source id to the list.
                    source_ids.append(report["source_id"])
        
            # If there is at least one report, send the reports to Thundermaps.
            if len(reports) > 0:
                # Upload 10 at a time.
                for some_reports in [reports[i:i+10] for i in range(0, len(reports), 10)]:
                    print("Sending %d reports..." % len(some_reports))
                    self.tm_obj.sendReports(account_id, some_reports)
                    time.sleep(3)
            # Save the posted source_ids.
            try:
                source_ids_file = open(".source_ids_store", "w")
                for i in source_ids:
                    source_ids_file.write("%s\n" % i)
                source_ids_file.close()
            except Exception as e:
                print("! WARNING: Unable to write cache file.")
                print("! If there is an old cache file when this script is next run, it may result in duplicate reports.")
        
            # Wait 1 hour before trying again.
            time.sleep(60 * 60 * 1)
            
updater = Updater(key, account_id)
updater.start()