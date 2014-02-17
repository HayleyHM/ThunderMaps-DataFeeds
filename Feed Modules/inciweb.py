#
#inciweb.py
#Module for pushing new InciWeb Incidents from the Incident Information System site. <http://inciweb.org/>
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import time
import xml.etree.ElementTree as ET
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps' 
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'inciweb-incidents'

class Incidents:
    def format_feed(self):
       #Retrieves the data feed and stores it as xml
        demolitions_file = urllib.request.urlretrieve('http://inciweb.nwcg.gov/feeds/rss/incidents/', 'inciweb_feed.xml')
        tree = ET.parse('inciweb_feed.xml')
        listings = []
        for item in tree.iter(tag='item'):
                if item.find('{http://www.georss.org/georss}point').text.strip() == '-':
                        continue
                else:
                        unique_id = item[6].text.split('/')
                        date_time = item[1].text
                        format_date = self.format_datetime(date_time)
                        incident_type = item.find('title').text.replace(')', '').split('(')                        
                        if 'fire' in incident_type[1].lower():
                                category_name = 'Fire'
                        elif 'flood' in incident_type[1].lower():
                                category_name = 'Flood'
                        elif 'emergency' in incident_type[1].lower():
                                category_name = 'Emergency'
                        else:
                                category_name = 'General Alert'
                        #format each parameter into json format for application use
                        listing = {"occurred_on":format_date, 
                                   "latitude":item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}lat').text, 
                                   "longitude":item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}long').text, 
                                   "description":item.find('title').text + '<br/>' + item.find('description').text,
                                   "category_name":category_name,
                                   "source_id":unique_id[-2]}
                        #create a list of dictionaries
                        listings.append(listing)            
        return listings
                
           
    def format_datetime(self, date_time):
            #convert date and time format to UTC
            date_time = date_time.split()
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            if date_time[2] in monthDict:
                    month = monthDict[date_time[2]]
            date_time = str(date_time[3]) + '-' + str(month) + '-' + str(date_time[1]) + ' ' + date_time[4] + date_time[5]
            return date_time

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
		
			# Wait 30 minutes before trying again.
			time.sleep(60 * 30)
			
updater = Updater(key, account_id)
updater.start()