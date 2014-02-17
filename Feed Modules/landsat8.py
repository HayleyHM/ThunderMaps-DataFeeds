#!/usr/bin/env python3
#
# This example shows how to take the newest data from an updating data feed and post it to ThunderMaps,
# while caching which data has already been posted to ThunderMaps.
# It should be used for a data feed that doesn't provide the ability to specifiy the start date for the data returned.
#
#Author: hayley.ahm@gmail.com>
#
import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Pthundermaps
import json

key = 'THUNDERMAPS_API_KEY' 
account_id = 'satellite'

class Incidents:
	def format_feed(self):
		#Retrieves the data feed and stores it as xml
		satellite_file = urllib.request.urlretrieve('http://landsat.usgs.gov/Landsat8.rss', 'landsat8_feed.xml')
		tree = ET.parse('landsat8_feed.xml')
		root = tree.getroot()
		listings = []
		for image in tree.iter(tag='item'):
			title = image.find('title').text.split()
			date = title[6] + ' ' + title[7]
			format_date = self.format_datetime(date)
			title = title[0] + ' ' + title[1] + ' ' + title[2] + ' ' + title[3] + " - Satellite Image"
			imagery_id = image.find('guid').text
			description = image.find('description').text.split('\n')
			satellite = description[4].strip('</a><br/>')
			cloud = description[5].split(',')
			cloud = cloud[2].strip('<br/>')
			scene_id = description[6]
			download = description[8].strip(' (Requires user registration.)')
			image_link = image.find('guid').text
			description = satellite + '<br/>' + scene_id + '<br/>' + title + '<br/>' + cloud + '<br/>Download requires user registration: ' + download
			# compile information into json format from application use
			listing = {"occurred_on":format_date, 
			          "latitude":image[4].text, 
			          "longitude":image[5].text, 
			          "description":description,
			          "source_id":imagery_id[-25:-4],
			          "attachment_url": image_link
			          }
			# create list of dictionaries
			listings.append(listing)
		return listings

	def format_datetime(self, date):
		# convert time format from GMT to UTC
		date_time = date.replace(' GMT', '').split('.')
		date_time = date_time[0]
		local = pytz.timezone("GMT")
		naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
		local_dt = local.localize(naive, is_dst = None)
		utc_dt = str(local_dt.astimezone(pytz.utc))
		return utc_dt
	
class Updater:
	def __init__(self, key, account_id):
		self.tm_obj = Pthundermaps.ThunderMaps(key)
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
					for report in some_reports:
						# Add image
						image_id = self.tm_obj.uploadImage(report["attachment_url"])
						if image_id != None:
							print("[%s] Uploaded image for listing %s..." % (time.strftime("%c"), report["source_id"]))
							report["attachment_ids"] = [image_id]
						del report["attachment_url"]
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