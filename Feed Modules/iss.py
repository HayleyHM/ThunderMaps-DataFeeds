'''This module uses an API built by Jim Anning <http://jimanning.com/2013/> to load and push the International Space Station position to the ThunderMaps Application

Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
Date: 18 February 2014'''

import requests
import time
import pytz, datetime
import sys
sys.path.append(r'/usr/local/thundermaps')
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'international-space-station'

class Incidents:
	def format_feed(self):
		#Retrieves the data feed and stores it as xml
		feed = requests.get('http://jimanning.com/issapi/')
		feed_dict = feed.json()
		capture_time = time.gmtime(int(feed_dict['tle']['epoch']))
		year, month, day, hour, minute, seconds = capture_time[:6]
		pub_date = self.format_datetime(year, month, day, hour, minute, seconds)
		#format each parameter into json format for application use
		listing = {"occurred_on":pub_date, 
			   "latitude":feed_dict['position']['lat'], 
			   "longitude":feed_dict['position']['lon'], 
			   "description":'International Space Station<br/>Orbital Speed: %s km per second' %feed_dict['position']['vel'] + '<br/>Altitude: %s km' %feed_dict['position']['alt'] + '<br/><a href="http://jimanning.com/2013/01/an-api-for-calculating-historic-positions-of-the-iss/">Click here for more information...</a>',
			   "source_id":feed_dict['tle']['epoch']}
		#create a list of dictionaries
		return listing
	
	def format_datetime(self, year, month, day, hour, minute, seconds):
		#convert date and time format from GMT to UTC
		if len(str(month)) == 1:
			month = '0' + str(month)
		date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute) + ':' + str(seconds)
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
			report = self.feed_obj.format_feed()
			# Create report for the listing.
			reports = []
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
		
			# Wait 1 hour before trying again.
			time.sleep(60 * 60 * 1)
			
updater = Updater(key, account_id)
updater.start()