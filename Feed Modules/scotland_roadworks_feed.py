'''This module formats the Scotland Roadworks - GeoRSS data feed taken from <www.trafficscotland.org> into a JSON 
format for ThunderMaps application use.

Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
Date: 9 January 2014'''

import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps' 
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'scotland-roadworks-alerts'

class Incidents:
    def format_feed(self):
        #retrieves the GeoRSS feed using the urllib.request library and stores as xml
        traffic_feed = urllib.request.urlretrieve('http://www.trafficscotland.org/rss/feeds/roadworks.aspx', 'incident_feed.xml')
        tree = ET.parse('incident_feed.xml')
        listings = []
        #iterates through the diffrent events and stores important information
        for item in tree.iter(tag='item'):
            unique_id = item.find('link').text.split('/')
            date = item.find('pubDate').text
            format_date = self.format_datetime(date)
            location = item[3].text.split()
            #format each parameter into JSON format for application use
            listing = {"occurred_on":format_date, 
                        "latitude":location[0], 
                        "longitude":location[1], 
                        "description":item.find('description').text.replace('<br />', '<br/>'),
                        "source_id": unique_id[3]}
            #create a list of dictionaries
            listings.append(listing)
        return listings
    
    def format_datetime(self, date):
                #convert date and time format from GMT to UTC
                date_time = date.split()
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
		
			# Wait 6 hours before trying again.
			time.sleep(60 * 60 * 6)
			
updater = Updater(key, account_id)
updater.start()