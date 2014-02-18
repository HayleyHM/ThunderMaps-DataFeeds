'''This module uses the API provided by the Helsinki Open Data project to retrieve and update ThunderMaps reports.

Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
Date: 18 February 2014'''

import requests
import pytz, datetime
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'helsinki-snowplow-alerts'

class Incidents:
	def format_feed(self):
		listings = []
		feed = requests.get('http://dev.hel.fi/aura/v1/snowplow/')
		json_feed = feed.json()
		# converts the api request into json format
		for entry in json_feed:
			time = entry['last_location']['timestamp'].replace('T', ' ')
			pubdate = self.format_datetime(time)
			activity_type = entry['last_location']['events'][0]
			if 'kv' in activity_type:
				category = 'Bicycle and Pedestrian Lanes'
			elif 'au' in activity_type:
				category = 'Snow Removal'
			elif 'su' in activity_type:
				category = 'De-icing with Salt'
			elif 'hi' in activity_type:
				category = 'Spreading Sand'
			else:
				category = 'Snowplow Work'
			#format each parameter for application use
			listing = {"occurred_on":pubdate, 
				   "latitude":entry['last_location']['coords'][1], 
				   "longitude":entry['last_location']['coords'][0], 
				   "description":'Helsinki Snowplow<br/>Plow ID: %s' %entry['id'],
			           "category_name": category,
				   "source_id":entry['last_location']['timestamp']}
			#create a list of dictionaries
			listings.append(listing)
		return listings
	
	def format_datetime(self, date_time):
		#convert date and time format from GMT to UTC
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
		
			# Wait 30 minutes before trying again.
			time.sleep(60 * 30)
            
updater = Updater(key, account_id)
updater.start()