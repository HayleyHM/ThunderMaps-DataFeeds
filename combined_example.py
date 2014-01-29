#!/usr/bin/env python3
#
# This example shows how to take the newest data from an updating data feed and post it to ThunderMaps,
# while caching which data has already been posted to ThunderMaps.
# It should be used for a data feed that doesn't provide the ability to specifiy the start date for the data returned.
#
#Author: Daniel Gibbs <danielgibbs.name>
#
import requests
import pytz, datetime
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #Grabs the Pthundermaps.py location for import
import Pthundermaps #thundermaps.py file with photo upload capabilities
import json

key = '<THUNDERMAPS_API_KEY>'
account_id = '<THUNDERMAPS_ACCOUNT_ID>'

class Incidents:
	def format_feed(self):
			listings = []
			photo_ids = self.get_photo_ids()
			# Uses the photo id's to grab the photo information from the GeoStock Photo's API
			for key,value in photo_ids.items():
				photo_params = {"id":key}
				photo_feed = requests.get('http://geostockphoto.com/photo/getInfo/apiKey/kRqJ2NgO', params=photo_params)
				try:
					info = photo_feed.json()
				except ValueError:
					print('continue')
					continue
				date = info['approvedDate']
				format_date = self.format_datetime(date)
				rank_id = info['rate']
				rank_id = "GeoStock Photo" + (" - Rank %s" %rank_id)
				listing = {"occurred_on":format_date, 
				           "latitude":info['lat'], 
				           "longitude":info['lng'], 
				           "description":str(info['title'].title()) + '<br/>' + 'User: ' + str(info['idUser']),
				           "category_name":rank_id,
				           "source_id":key,
				           "attachment_url":value
				        }
				listings.append(listing)
			return listings

	def get_photo_ids(self):
		# Uses the GeoStock Photos API to grab photo id's and thumbnail images
		search_params = {"thumb":"430"}
		search_feed = requests.get('http://geostockphoto.com/photo/getSearch/apiKey/kRqJ2NgO', params=search_params)
		all_photos = search_feed.json()
		for photo in all_photos["photo"]:
			# Stores the photo id's and images in a dict
			photo_ids = {photo["id"]:photo["src"]}
		return photo_ids
	
	def format_datetime(self, date):
		#convert date and time format from GMT to UTC
		date_time = date.replace('/', ' ').split()
		monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
		if date_time[1] in monthDict:
			month = monthDict[date_time[1]]
		date_time = str(date_time[2]) + '-' + str(month) + '-' + str(date_time[0]) + ' ' + str(date_time[4])
		local = pytz.timezone("GMT")
		naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
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
		
			# Wait 30 minutes before trying again.
			time.sleep(60 * 30)
			
updater = Updater(key, account_id)
updater.start()