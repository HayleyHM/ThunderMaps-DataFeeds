#!/usr/bin/env python3
#
# This example shows how to take the newest data from an updating data feed and post it to ThunderMaps,
# while caching which data has already been posted to ThunderMaps.
# It should be used for a data feed that doesn't provide the ability to specifiy the start date for the data returned.
#
# Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
#
import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps' 
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'
account_id = 'THUNDERMAPS_ACCOUNT_ID'

class Incidents:
	def format_feed(self):
			#Retrieves the data feed and stores it as xml
			dispatch_file = urllib.request.urlretrieve('http://www.portlandonline.com/scripts/911incidents.cfm', 'dispatch_feed.xml')
			tree = ET.parse('dispatch_feed.xml')
			listings = []
			for entry in tree.iter('{http://www.w3.org/2005/Atom}entry'):
				location = entry[6].text.split()
				dispatch_id = entry[0].text
				dispatch_title = entry[4].attrib
				address = entry[3].text.split('at ')
				final_address = address[1].split(' [')
				agency = final_address[1].replace(']', '').split('#')
				category = dispatch_title['label']
				if 'medical' in category.lower():
					main_category = "Medical"
				elif 'civil' in category.lower() or 'welfare' in category.lower() or 'citizen' in category.lower():
					main_category = 'Civil'
				elif 'theft' in category.lower() or 'stolen' in category.lower():
					main_category = 'Theft'
				elif 'alarm' in category.lower() or 'premise' in category.lower():
					main_category = 'Security Check'
				elif 'accident' in category.lower():
					main_category = 'Accident'
				elif 'assault' in category.lower() or 'disturbance' in category.lower() or 'threat' in category.lower():
					main_category = 'Violence'
				elif 'hazard' in category.lower():
					main_category = "Hazard"
				elif 'animal' in category.lower():
					main_catergory = 'Animal'
				else:
					main_category = 'General Duties'
				#format each parameter into json format for use with applications
				listing = {"occurred_on":entry[5].text.replace('T', ' ').replace('.0', ''), 
					   "latitude":location[0], 
					   "longitude":location[1], 
					   "description":category.title() + '<br/>' + 'Location: ' + final_address[0].replace(', OR', '').title().strip(),
					   "primary_category_name": main_category.title(),
					   "secondary_category_name": agency[0].strip(),
					   "source_id":dispatch_id[-13:]}
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
		
			# Wait 30 minutes before trying again.
			time.sleep(60 * 30)
			
updater = Updater(key, account_id)
updater.start()