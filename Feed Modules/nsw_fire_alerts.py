#
#fire_alerts.py
#Module for formatting new New South Wales Rural Fire Alerts.
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#
import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps' 
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'nsw-rural-fire-incidents'

class Incidents:
	def format_feed(self):
		#Retrieves the data feed and stores it as xml
		dispatch_file = urllib.request.urlretrieve("http://www.rfs.nsw.gov.au/feeds/majorIncidents.xml", 'fire_alerts.xml')
		tree = ET.parse('fire_alerts.xml')
		listings = []
		for item in tree.iter(tag='item'):
			incident_id = item[3].text.split(':')
			location = item[6].text.split()
			summary = item.find("description").text.split('<br />')
			date_time = summary[-1][9:]
			format_date = self.format_datetime(date_time)
			if 'grass' in summary[4].lower() or 'scrub' in summary[4].lower() or 'forest' in summary[4].lower() or 'haystack' in summary[4].lower():
				primary_category = 'Forest, Scrub & Grass'
			elif 'vehicle' in summary[4].lower():
				primary_category = 'Vehicle'
			elif 'structure' in summary[4].lower() or 'shed' in summary[4].lower():
				primary_category = 'Structure'
			elif 'hazard' in summary[4].lower() or 'storm' in summary[4].lower():
				primary_category = 'Hazard'
			elif 'alarm' in summary[4].lower():
				primary_category = 'Alarm'
			elif 'assist' in summary[4].lower():
				primary_category = 'Assist & Rescue'
			elif 'fire' in summary[4].lower():
				primary_category = 'Fire'
			else:
				primary_category = 'Dispatch Call Out'
			agency = summary[7].replace('RESPONSIBLE AGENCY: ', '')
			#format each parameter into json format for application use
			listing = {"occurred_on":format_date, 
				   "latitude":location[0], 
				   "longitude":location[1], 
				   "description":summary[4].title() + '<br/>' + item[0].text.title() + ' - ' + summary[3][8:].title() + '<br/>' + summary[6].title() + '<br/>' + summary[1].title(),
				   "primary_category_name":primary_category,
				   "secondary_category_name": agency,
				   "source_id":incident_id[2]}
			#create a list of dictionaries
			listings.append(listing)
		return listings
        
	def format_datetime(self, date_time):
		#convert date and time format from EST to UTC
		date_time = date_time.split()
		monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
		if date_time[1] in monthDict:
			month = monthDict[date_time[1]]
		date_time = str(date_time[2]) + '-' + str(month) + '-' + str(date_time[0]) + ' ' + str(date_time[3])
		local = pytz.timezone("Australia/NSW")
		naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
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
		
			# Wait 20 minutes before trying again.
			time.sleep(60 * 20)
			
updater = Updater(key, account_id)
updater.start()