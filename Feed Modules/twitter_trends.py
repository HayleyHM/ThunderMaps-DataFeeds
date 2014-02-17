#
#incidents.py
#Module for pushing new Twitter Trends updates through to users on ThunderMaps.com
#
#Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
#

import time
import pytz, datetime
from twitter import *
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'trending-on-twitter'

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
oauth_token = ''
oauth_secret = ''


class Incidents:
	def format_feed(self):
		listings = []
		trends = self.trending()
		for i in trends:
			# Uses search/tweets api to find english tweets with the trending query
			twitter = Twitter(api_version='1.1', auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))
			tweets = twitter.search.tweets(geocode='46.0000,7.0000,6500km', count='100', q=i, lang='en')
			for j in tweets['statuses']:
				counter = 0
				# removes any tweets with absent location data
				if j['coordinates'] != None:
					location_dict = j["geo"]
					location = location_dict["coordinates"]
					user = j['user']
					date = j['created_at']
					format_date = self.format_datetime(date)
					text = j['text']#.split()
					username = user["screen_name"]
					user_link = '<a href="https://twitter.com/' + username + '">%s</a>' %username
					# compile information into json format for application use
					listing = {"occurred_on":format_date, 
					           "latitude":location[0], 
					           "longitude":location[1], 
					           "description": user_link + '<br/>' + text.title(),
					           "source_id":j['id']
						}
					listings.append(listing)
				else:
					counter += 1
					continue
		print("%s tweets did not contain location data" % counter)
		return listings
		
        
	def format_datetime(self, date_time):
		#convert date and time format to UTC
		date_time = date_time.split()
		monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
		if date_time[1] in monthDict:
			month = monthDict[date_time[1]]
		date_time = str(date_time[5]) + '-' + str(month) + '-' + str(date_time[2]) + ' ' + str(date_time[3] + str(date_time[4]))
		return date_time

	def trending(self):
		# find trending topics on twitter using oauth
		trends_list = []
		twitter = Twitter(api_version='1.1', auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))
		tweets = twitter.trends.place(_id=1)
		for i in tweets:
			for j in i['trends']:
				trends_list.append(j['name'])
		return trends_list
	
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
		
			# Wait 2 hours before trying again.
			time.sleep(60 * 60 * 2)
			
updater = Updater(key, account_id)
updater.start()