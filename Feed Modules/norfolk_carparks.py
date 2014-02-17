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
account_id = 'norfolk-england-car-park-tracker'

class Incidents:
	def format_feed(self):
		carpark_feed = urllib.request.urlretrieve('http://datex.norfolk.cdmf.info/carparks/content.xml', 'parks_feed.xml')
		tree = ET.parse('parks_feed.xml')
		listings = []
		url = '{http://datex2.eu/schema/1_0/1_0}'
		for item in tree.iter(tag=url + 'situation'):
			carpark_id = item.attrib["id"]
			for j in item.iter(url + 'situationRecord'):
				taken = j.find(url + 'occupiedSpaces').text
				total = j.find(url + 'totalCapacity').text
				carparks = int(total) - int(taken)
				if carparks == 0:
					carparks = "no"
				else:
					carparks = str(carparks)
				date = j.find(url + 'situationRecordCreationTime').text.replace('T', ' ')
				format_date = self.format_datetime(date)
				name = j.find(url + 'carParkStatus').text
				carpark_status = re.sub('([A-Z]+)', r' \1', name).title()
			for elem in item.iter(tag=(url+'pointCoordinates')):
				latitude = elem.find(url + 'latitude').text
				longitude = elem.find(url + 'longitude').text
			for elem in item.iter(tag=(url+'referencePoint')):
				street = elem.find(url + 'roadName').text.title()
			# compiles information into json format for application use
			listing = {"occurred_on":format_date, 
		                   "latitude":latitude, 
		                   "longitude":longitude, 
		                   "description":'There are %s remaining spaces available...' %carparks,
		                   "category_name":carpark_status,
		                   "source_id":carpark_id}
			#create a list of dictionaries
			listings.append(listing)
		return listings   
            
            
	def format_datetime(self, date):
		#convert date and time format from EST to UTC
		local = pytz.timezone("EST")
		naive = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
		local_dt = local.localize(naive, is_dst = None)
		utc_dt = local_dt.astimezone(pytz.utc)
		utc_dt = str(utc_dt)
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
		
			# Wait 15 minutes before trying again.
			time.sleep(60 * 15)
			
updater = Updater(key, account_id)
updater.start()