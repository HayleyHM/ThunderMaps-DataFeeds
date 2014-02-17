#!/usr/bin/env python3
#
# This example shows how to take the newest data from an updating data feed and post it to ThunderMaps,
# while caching which data has already been posted to ThunderMaps.
# It should be used for a data feed that doesn't provide the ability to specifiy the start date for the data returned.
#
#Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
#
import requests
import pytz, datetime
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Wthundermaps
import json

key = 'THUNDERMAPS_API_KEY'
account_id = 'nz-eventfinda-events'

class Incidents:
	def format_feed(self):
		listings = []
		#Retrieves and formats the event data from EventFinda's API ... Authentication is required
		authentication = ('USERNAME', 'PASSWORD')
		headers={
		    "X-Mashape-Authorization": "MASHAPE_KEY"
		  }    
		event_feed = requests.get("https://eventfinda-eventfinda-nz.p.mashape.com/events.json", auth=authentication, headers=headers)
		event_info = event_feed.json()
		for event in event_info['events']:
			#Formats the required data into reports
			location = event['point']
			date = event['datetime_start']
			format_date = self.format_datetime(date)
			link = event['url']
			event_url = '<a href="' + str(link) + '">here</a>'
			description = event['name'].upper() + '<br/>' + 'Entry Restrictions: '+ event['restrictions'] + '<br/>' + event['description'] + '<br/>' + 'Click %s for more information.' % event_url
			event_type = event['category']
			#Converts the data into JSON format for application use
			listing = {"occurred_on":format_date, 
		                   "latitude":location['lat'], 
		                   "longitude":location['lng'], 
		                   "description":description,
		                   "category_name":event_type['name'],
		                   "source_id":event['id']}
			listings.append(listing)
		return listings
                
	def format_datetime(self, date):
                #convert date and time format from GMT to UTC
                local = pytz.timezone("GMT")
                naive = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
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
		
			# Wait 6 hours before trying again.
			time.sleep(60 * 60 * 6)
			
updater = Updater(key, account_id)
updater.start()