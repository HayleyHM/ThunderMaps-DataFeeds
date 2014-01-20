#!/usr/bin/env python3
#
# This example shows how to take the newest data from an updating data feed and post it to ThunderMaps,
# while caching which data has already been posted to ThunderMaps.
# It should be used for a data feed that doesn't provide the ability to specifiy the start date for the data returned.
#
#Author: Daniel Gibbs <danielgibbs.name>
#
import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET
import sys
sys.path.append(r'/usr/local/thundermaps')
import Wthundermaps
import html.parser

class Dispatch:
	def format_feed(self):
		h = html.parser.HTMLParser()
		dispatch_file = urllib.request.urlretrieve('http://www.dot.nd.gov/travel-info-v2/georss/workzones.xml', 'workzones.xml')
		tree = ET.parse('workzones.xml')
		listings = []
		for entry in tree.iter('{http://www.w3.org/2005/Atom}entry'):
				try: 
						location = entry.find('{http://www.georss.org/georss}point').text.split()
				except:
						location = entry.find('{http://www.georss.org/georss}line').text.split()
				work_id = entry.find('{http://www.w3.org/2005/Atom}id').text
				date = entry.find('{http://www.w3.org/2005/Atom}updated').text.replace('T', ' ')
				summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
				format_summary = h.unescape(summary).replace('<strong>', '-').replace('</strong>', '').split('-')
				description = ''
				for i in format_summary:
						i = i.strip()
						description += i + '\n'
				work_type = format_summary[1].strip().split(':')
				#format each parameter into a dictionary
				listing = {"occurred_on":date, 
		                           "latitude":location[0], 
		                           "longitude":location[1], 
		                           "description":description,  
		                           "category_name":'North Dakota Roadworks - ' + work_type[1].title(),
		                           "source_id":work_id}
				#create a list of dictionaries
				listings.append(listing)
		return listings				
	
class Updater:
	def __init__(self, key, account_id):
		self.tm_obj = thundermaps.ThunderMaps(key)
		self.feed_obj = Dispatch()
		self.account_id = account_id
		
	def start():
		feed = Dispatch()
		key = '<YOUR_API_KEY_HERE>'
		account_id = '<THUNDERMAPS_ACCOUNT_ID>'
		# Create an instance of ThunderMaps
		tm = Wthundermaps.ThunderMaps(key)
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
			items = feed.format_feed()
		
			# Create reports for the listings.
			reports = []
			for report in items:
				# Add the report to the list of reports if it hasn't already been posted.
				if report["source_id"] not in source_ids:
					reports.append(report)
					print("Adding %s" % report["description"])
					# Add the source id to the list.
					source_ids.append(report["source_id"])
		
			# If there is at least one report, send the reports to Thundermaps.
			if len(reports) > 0:
				# Upload 10 at a time.
				for some_reports in [reports[i:i+10] for i in range(0, len(reports), 10)]:
					print("Sending %d reports..." % len(some_reports))
					tm.sendReports(account_id, some_reports)
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
		
			# Wait 10 minutes before trying again.
			time.sleep(60 * 10)
			
Updater.start()