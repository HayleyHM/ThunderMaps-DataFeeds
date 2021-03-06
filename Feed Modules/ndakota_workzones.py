#!/usr/bin/env python3
#
# This example shows how to take the newest data from an updating data feed and post it to ThunderMaps,
# while caching which data has already been posted to ThunderMaps.
# It should be used for a data feed that doesn't provide the ability to specifiy the start date for the data returned.
#
#Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
#
import urllib.request
import time
import xml.etree.ElementTree as ET
import sys
sys.path.append(r'/usr/local/thundermaps')#r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Wthundermaps
import re

key = 'THUNDERMAPS_API_KEY'  
account_id = 'north-dakota-roadworks-alerts'

class Incidents:
	def format_feed(self):
		dispatch_file = urllib.request.urlretrieve('http://www.dot.nd.gov/travel-info-v2/georss/workzones.xml', 'workzones.xml')
		tree = ET.parse('workzones.xml')
		listings = []
		for entry in tree.iter('{http://www.w3.org/2005/Atom}entry'):
			try: 
					location = entry.find('{http://www.georss.org/georss}point').text.split()
			except:
					location = entry.find('{http://www.georss.org/georss}line').text.split()
			condition_id = entry.find('{http://www.w3.org/2005/Atom}id').text
			date = entry.find('{http://www.w3.org/2005/Atom}updated').text.replace('T', ' ')
			description = re.sub('<[^>]*>', ' ', entry.find('{http://www.w3.org/2005/Atom}summary').text)
			summary = description.replace('&nbsp;&nbsp;&nbsp;', '<br/>').replace('&nbsp;', ' ')
			#format each parameter into json format for application use
			listing = {"occurred_on":date, 
		                   "latitude":location[0], 
		                   "longitude":location[1], 
		                   "description":summary.title(),
		                   "source_id":condition_id}
			#create a list of dictionaries
			listings.append(listing)
		return listings			
	
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
		
			# Wait 2 hours before trying again.
			time.sleep(60 * 60 * 2)
			
updater = Updater(key, account_id)
updater.start()