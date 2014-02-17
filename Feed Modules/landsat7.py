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
import Pthundermaps
import json

key = 'THUNDERMAPS_API_KEY'  
account_id = 'usgs-landsat-7-imagery'

class Incidents:
	def format_feed(self):
		#Retrieves the data feed and stores it as xml
		image_file = urllib.request.urlretrieve("http://landsat.usgs.gov/Landsat7.rss", 'landsat_feed.xml')
		tree = ET.parse('landsat_feed.xml')     
		listings = []
		for item in tree.iter(tag='item'):
			imagery_name = item[0].text.split()
			imagery_name = imagery_name[0] + ' ' + imagery_name[1] + ' ' + imagery_name[2] + ' ' + imagery_name[3]
			summary = item[2].text.split('\n')
			imagery_id = summary[-2][10:]
			path_row = summary[5].split(',')
			imagery_position = path_row[0] + ' -' + path_row[1] + " - Satellite Image"
			download = '<a href="http://earthexplorer.usgs.gov/"><strong>Earth Explorer</strong></a>'
			description = summary[4][:19] + '<br/>' + imagery_id + '<br/>' + imagery_position + '<br/>' + path_row[2][1:-5] + '<br/>' + '<br/>Download requires user registration: ' + download
			date_time = item[0].text
			format_date = self.format_datetime(date_time)
			jpeg_link = item.find('guid').text
			#format each parameter into a dictionary
			listing = {"occurred_on":format_date, 
				   "latitude":item[4].text, 
				   "longitude":item[5].text, 
				   "description":description,
				   "category_name":'Landsat 7 Satellite Image',
				   "source_id":imagery_id,
				   "attachment_url":jpeg_link}
			#create a list of dictionaries
			listings.append(listing)
		return listings

	def format_datetime(self, date_time):
		#convert date and time format from GMT to UTC
		date_time = date_time.replace(' GMT', '').split()
		date_time = date_time[4] + ' ' + date_time[6]
		local = pytz.timezone("GMT")
		naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
		local_dt = local.localize(naive, is_dst = None)
		utc_dt = local_dt.astimezone(pytz.utc)
		utc_dt = str(utc_dt)
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