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
from geopy import geocoders
import time
import re
import uuid
import sys
sys.path.append(r'/usr/local/thundermaps') 
import Wthundermaps


key = 'THUNDERMAPS_API_KEY'  
account_id = 'kent-england-fire-incidents'

class Incidents:
	def format_feed(self, source_ids):
		#Retrieves the data feed and stores it as xml
		urllib.request.urlretrieve("http://www.kent.fire-uk.org/IncidentListRss.aspx", 'kent_fires.xml')
		tree = ET.parse('kent_fires.xml')
		listings = []
		for entry in tree.iter(tag='item'):
			source_id = entry.find('guid').text
			# Checks current source_ids to avoid geocoder duplication
			if source_ids != None:
				if source_id in source_ids:
					print('Source ID: %s already taken' %source_id)
					pass
				else:
					pass			
			summary = re.sub('<[^>]*>', ' ', (entry.find('description').text))
			event = summary.split(' ', 1)
			description = event[1].split(' Address : ')
			address = description[1].split(' Attendance : ')
			location = self.geocoder(address[0] + ', England')
			if location == None:
				pass
			else:
				date = entry.find('pubDate').text
				format_date = self.format_datetime(date)
				attendance = address[1].split('Stop Time : ')
				title = entry.find('title').text.lower()
				if 'flood' in title:
					main_category = 'Flood'
				elif 'car' in title or 'crash' in title or 'rtc' in title or 'vehicle' in title:
					main_category = 'Vehicle Accident'				
				elif 'fire' in title or 'alight' in title or 'smoke' in title:
					main_category = 'Fire'
				elif 'gas' in title:
					main_category = 'Gas Leak'
				elif 'rescue' in title:
					main_category = 'Search & Rescue'
				else:
					main_category = 'Dispatch Call Out'
				# format each parameter into json format for application use
				listing = {"occurred_on":format_date, 
				           "latitude":location[0], 
				           "longitude":location[1], 
				           "description": title.title() + '<br/>' + description[0] + '<br/>' + 'Attendance: %s' %attendance[0],
				           "category_name":main_category,
				           "source_id":source_id
				        }
				listings.append(listing)
			time.sleep(2)
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

	def geocoder(self, address):
		#Geocodes addresses using the GoogleV3 package. This converts addresses to lat/long pairs
		try:
			g = geocoders.GoogleV3()
			street, (lat, long) = g.geocode(address, timeout=5)
			if (lat, long) == 'None':   
				pass
			else:
				return lat, long
		except TypeError:
			pass 
	
class Updater:
	def __init__(self, key, account_id):
		self.tm_obj = Wthundermaps.ThunderMaps(key)
		self.feed_obj = Incidents()
		self.account_id = account_id
		
	def start(self):
		# Try to load the source_ids already posted.
		source_ids = []
		try:
			source_ids_file = open("_ids.source_ids_store", "r")
			for i in source_ids_file.readlines():
				source_ids.append(i.strip())
			source_ids_file.close()
		except Exception as e:
			print("! WARNING: No valid cache file was found. This may cause duplicate reports.")

		# Run until interrupt received.
		while True:
			# Load the data from the data feed.
			# This method should return a list of dicts.
			items = self.feed_obj.format_feed(source_ids)
			# Create reports for the listings.
			reports = []
			for report in items:
				# Add the report to the list of reports if it hasn't already been posted.
				if report["source_id"] not in source_ids:
					reports.append(report)
					print("Adding %s" % report["source_id"])
					# Add the source id to the list.
					source_ids.append(report["source_id"])
		
			# If there is at least one report, send the reports to Thundermaps.
			if len(reports) > 0:
				# Upload 10 at a time.
				for some_reports in [reports[i:i+10] for i in range(0, len(reports), 10)]:
					print("Sending %d reports..." % len(some_reports))
					self.tm_obj.sendReports(account_id, some_reports)
					time.sleep(3)
			else:
				print('No new reports...')
			# Save the posted source_ids.
			try:
				source_ids_file = open("_ids.source_ids_store", "w")
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