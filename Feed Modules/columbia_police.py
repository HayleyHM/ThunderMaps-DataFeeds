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
import html

key = 'THUNDERMAPS_API_KEY'  
account_id = 'columbia-911-police-dispatch'

class Incidents:
	def format_feed(self):
		#Uses the urllib.request library to import the GeoRSS feed and saves as xml
		incident_feed = urllib.request.urlretrieve('http://www.gocolumbiamo.com/PSJC/Services/911/911dispatch/police_georss.php//eqcenter/catalogs/rssxsl.php?feed=eqs7day-M5.xml', 'Columbia_dispatch.xml')
		xml_data = open('Columbia_dispatch.xml', 'r+')
		#Creates a new xml file called 'Dispatch_fixed.xml' to write special character corrections
		format_xml = open('Dispatch_fixed.xml', 'w')
		for line in xml_data.readlines():
			if 'C&I' in line:
				line = html.escape(line)
				format_xml.write(line)
			else:
				format_xml.write(line)
		format_xml.close()
		tree = ET.parse('Dispatch_fixed.xml')
		listings = []
		#Iterates through each incident in the feed and extracts useful information
		for item in tree.iter(tag='item'):
			#formats each parameter into a JSON format for application use
			date = item.find('pubDate').text
			format_date = self.format_datetime(date)
			category = item.find('title').text
			if 'medical' in category.lower() or 'overdose' in category.lower():
				main_category = "Medical"
			elif 'civil' in category.lower() or 'welfare' in category.lower() or 'citizen' in category.lower():
				main_category = 'Civil'
			elif 'burglary' in category.lower() or 'fraud' in category.lower() or 'theft' in category.lower() or 'robbery' in category.lower() or 'forgery' in category.lower():
				main_category = 'Burglary & Fraud'
			elif 'alarm' in category.lower() or 'check' in category.lower() or 'trespass' in category.lower():
				main_category = 'Security Check'
			elif 'accident' in category.lower() or 'vechile' in category.lower() or 'parking' in category.lower() or 'traffic' in category.lower():
				main_category = 'Vechile Incident'
			elif 'assault' in category.lower() or 'disturbance' in category.lower() or 'threat' in category.lower() or 'abuse' in category.lower() or 'harassment' in category.lower():
				main_category = 'Violence'
			elif 'missing' in category.lower() or 'suspicious' in category.lower():
				main_category = "Suspicious or Missing Person"
			elif 'vandalism' in category.lower() or 'litter' in category.lower():
				main_category = 'Animal'
			else:
				main_category = 'General Duties'			
			listing = {"occurred_on":format_date, 
				    "latitude":item.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}lat').text, 
				    "longitude":item.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}long').text, 
				    "description": item.find('title').text.title() + '<br/>' + item.find('description').text.title(),
				    "category_name": main_category,
				    "source_id":item.find('.//{http://www.gocolumbiamo.com/PSJC/Services/911/911dispatch/calldatachema.php#}InNum').text}
			#create a list of dictionaries
			listings.append(listing)
		return listings        
    
	def format_datetime(self, date):
		#convert date and time format from CST to UTC
		date_time = date.split()
		monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
		if date_time[2] in monthDict:
			month = monthDict[date_time[2]]
		date_time = str(date_time[3]) + '-' + str(month) + '-' + str(date_time[1]) + ' ' + str(date_time[4])
		local = pytz.timezone("CST6CDT")
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