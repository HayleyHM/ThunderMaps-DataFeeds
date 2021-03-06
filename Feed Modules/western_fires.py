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
import re

key = 'THUNDERMAPS_API_KEY'  
account_id = 'western-australia-incidents'

class Incidents:
	def format_feed(self):
		#Retrieves the data feed and stores it as xml
		urllib.request.urlretrieve("http://www.dfes.wa.gov.au/alerts/_layouts/fesa.sps2010.internet/fesalistfeed.aspx?List=e2064c8d-e111-41e1-8925-d249098d1a5e&View=b26d1f1b-0afc-4a65-8592-1c31c3af1323", 'west_fires.xml')
		tree = ET.parse('west_fires.xml')
		listings = []
		for entry in tree.iter(tag='item'):
			date = entry.find('pubDate').text
			format_date = self.format_datetime(date)
			description = entry.find('description').text
			category = description.replace('</b>', '-').replace('</div', '-').split('-')
			try:
				latitude = entry.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}lat').text
				longitude = entry.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}long').text
			except AttributeError:
				continue
			summary = re.sub('<[^>]*>', ' ', description)
			if 'grass' in category[1].lower() or 'scrub' in category[1].lower() or 'bush' in category[1].lower():
				main_category = 'Grass & Bush Fire'
			elif 'assist' in category[1].lower() or 'incident' in category[1].lower() or 'rescue' in category[1].lower():
				main_category = 'Incident & Rescue'
			elif 'structure' in category[1].lower() or 'car' in category[1].lower():
				main_category = 'Structure & Vehicle'
			elif 'non structure' in category[1].lower():
				main_category = 'Non Structure'
			elif 'fire' in category[1].lower():
				main_category = 'Fire'
			elif 'medical' in category[1].lower():
				main_category = 'Medical'
			else:
				main_category = 'Dispatch Call Out'		
			# format each parameter into JSON format for application use
			listing = {"occurred_on":format_date, 
				        "latitude":latitude, 
				        "longitude":longitude, 
				        "description": summary.strip().replace('\n', '<br/>'),
				        "category_name":main_category,
				        "source_id":entry.find('guid').text
				        }
			listings.append(listing)
		return listings
            
	            
	def format_datetime(self, date_time):
		#convert date and time format from GMT to UTC
		date_time = date_time.split()
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
		
			# Wait 20 minutes before trying again.
			time.sleep(60 * 20)
			
updater = Updater(key, account_id)
updater.start()