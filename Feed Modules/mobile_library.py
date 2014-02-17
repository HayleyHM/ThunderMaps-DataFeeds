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
from geopy import geocoders

key = 'THUNDERMAPS_API_KEY'  
account_id = 'christchurch-mobile-libraries'

class Incidents:
	def format_feed(self):
		#Retrieves the data feed and stores it as xml
		urllib.request.urlretrieve("http://www.trumba.com/calendars/Mobile.rss", 'mobile_library.xml')
		tree = ET.parse('mobile_library.xml')
		listings = []
		for item in tree.iter(tag='item'):
			summary = item[1].text.split('<br/>')
			address = summary[0]
			title_address = item[0].text
			if title_address[0] != 'New Year':
				title_address = title_address[0].strip() + ', Christchurch'
				location = self.geocoder(address, title_address)
				if location == None:
					continue
				date_time = item[5].text
				format_date = self.format_datetime(date_time)
				unique_id = item[2].text.split('%')
				title = item[0].text
				if 'Mobile ' in title:
					start = title.index('Mobile ')
					end = start + 8
					mobile_title = "Christchurch Mobile Library - " + title[start:end]
				else:
					mobile_title = "Chirstchurch Mobile Library"
				description = summary[1].replace('&nbsp;&ndash;&nbsp;', ' until ')
				link = '<a href="http://christchurchcitylibraries.com/mobiles/">Christchurch City Libraries</a>'
				#format each parameter into json format for application use
				listing = {"occurred_on":format_date, 
				       "latitude":location[1][0], 
				       "longitude":location[1][1], 
				       "description":description + '\n' + 'For more information go to: %s' %link,
				       "category_name":mobile_title,
				       "source_id":unique_id[-1]
				       }
				listings.append(listing)
			return listings
            
	def geocoder(self, address, title_address):
		#Geocodes addresses using the GoogleV3 package. This converts addresses to lat/long pairs
		weekdays = {1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday', 7:'Sunday'}
		checker = address.split(',')
		if checker[0] in weekdays.values():
			try:
				g = geocoders.GoogleV3()
				(lat, long) = g.geocode(title_address)
				if (lat, long) == 'None':
					pass
				else:
					return (lat, long)
			except TypeError:
				pass
		else:
			try:
				g = geocoders.GoogleV3()
				(lat, long) = g.geocode(address)
				if (lat, long) == 'None':   
					pass
				else:
					return (lat, long)
			except TypeError:
				pass 
           
            
	def format_datetime(self, date_time):
        #convert date and time format from GMT to UTC
		date_time = date_time.replace(' GMT', '').split()
		monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
		if date_time[1] in monthDict:
			month = monthDict[date_time[1]]
		date_time = str(date_time[2]) + '-' + str(month) + '-' + str(date_time[0]) + ' ' + str(date_time[3])
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
		
			# Wait 6 hours before trying again.
			time.sleep(60 * 60 * 6)
			
updater = Updater(key, account_id)
updater.start()