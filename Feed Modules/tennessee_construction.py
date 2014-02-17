#!/usr/bin/env python3
#
# This example shows how to take the newest data from an updating data feed and post it to ThunderMaps,
# while caching which data has already been posted to ThunderMaps.
# It should be used for a data feed that doesn't provide the ability to specifiy the start date for the data returned.
#
#Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
#
import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps' 
import Wthundermaps

key = 'THUNDERMAPS_API_KEY' 
account_id = 'tennessee-roadworks'

class Incidents:
	def format_feed(self):
		#Uses the urllib.request library to import the GeoRSS feed and saves as xml
		construction_feed = urllib.request.urlretrieve('http://ww2.tdot.state.tn.us/tsw/GeoRSS/TDOTConstructionGeorss.xml', 'tennessee_construction.xml')
		tree = ET.parse('tennessee_construction.xml')
		listings = []
		#Scans through each event in the feed and extracts useful information
		for item in tree.iter(tag='item'):
				title = item.find('title').text.split(' -')
				date = item.find('.//{http://www.tdot.state.tn.us/tdotsmartway/}BeginDate').text
				format_date = self.format_datetime(date)
				location = item.find('marker').text.split()
				region = item.find('.//{http://www.tdot.state.tn.us/tdotsmartway/}COUNTY').attrib['{http://www.tdot.state.tn.us/tdotsmartway/}REGION']
				if region == '1':
					category = 'Region 1: Knoxville'
				elif region == '2':
					category = 'Region 2: Chattanooga'
				elif region == '3':
					category = 'Region 3: Nashville'
				elif region == '4':
					category = 'Region 4: Jackson & Memphis'
				else:
					category = 'Tennessee'
				#formats each parameter into a JSON format for application use
				listing = {"occurred_on":format_date, 
					   "latitude":location[0], 
					   "longitude":location[1], 
					   "description":item.find('description').text,
					   "primary_category_name": category,
					   "source_id":item.find('guid').text}
				#create a list of dictionaries
				listings.append(listing)
		return listings
    
    
	def format_datetime(self, date):
		#convert date and time format from CST to UTC
		date_time = date.replace('/', ' ').split()
		date_time = str(date_time[2]) + '-' + str(date_time[0]) + '-' + str(date_time[1]) + ' ' + str(date_time[3])
		local = pytz.timezone("CST6CDT")
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