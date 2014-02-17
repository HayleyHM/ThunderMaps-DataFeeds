"""This module uses a Fire 911 Dispatch - GeoRSS feed from the Columbia City Government to format the data for the ThunderMaps Application. 

Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
Date: 09 January 2014"""

import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps') #r'/usr/local/thundermaps' 
import Sthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'columbia-911-emergency-dispatch'

class Incidents:
    def format_feed(self):
        #Uses the urllib.request library to import the GeoRSS feed and saves as xml
        incident_feed = urllib.request.urlretrieve('http://www.gocolumbiamo.com/PSJC/Services/911/911dispatch/fire_georss.php/eqcenter/catalogs/rssxsl.php?feed=eqs7day-M5.xml', 'Columbia_fire.xml')
        tree = ET.parse('Columbia_fire.xml')
        listings = []
        #Iterates through each incident in the feed and extracts useful information
        for item in tree.iter(tag='item'):
                #formats each parameter into a JSON format for application use
                date = item.find('pubDate').text
                format_date = self.format_datetime(date)
                if 'rescue' in item.find('title').text.lower() or 'assist' in item.find('title').text.lower() or 'aid' in item.find('title').text.lower():
                        primary_category = 'Assist & Rescue'
                elif 'medical' in item.find('title').text.lower():
                        primary_category = 'Medical'
                elif 'transport' in item.find('title').text.lower():
                        primary_category = 'Transport'
                elif 'training' in item.find('title').text.lower():
                        primary_category = 'Training'
                elif 'alarm' in item.find('title').text.lower():
                        primary_category = 'Alarm'
                elif 'gas leak' in item.find('title').text.lower() or 'hazard' in item.find('title').text.lower():
                        primary_category = 'Hazard'
                elif 'accident' in item.find('title').text.lower():
                        primary_category = 'Accident'
                elif 'permit' in item.find('title').text.lower():
                        primary_category = 'Permit'
                elif 'fire' in item.find('title').text.lower():
                        primary_category = 'Fire'            
                else:
                        primary_category = "Dispatch Call Out"
                agency = item.find('.//{http://www.gocolumbiamo.com/PSJC/Services/911/911dispatch/calldatachema.php#}Agencies').text
		# compile information into json format for application use
                listing = {"occurred_on":format_date, 
                            "latitude":item.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}lat').text, 
                            "longitude":item.find('.//{http://www.w3.org/2003/01/geo/wgs84_pos#}long').text, 
                            "description": item.find('description').text,
                            "primary_category_name": primary_category,
                            "secondary_category_name": agency,
                            "source_id":item.find('.//{http://www.gocolumbiamo.com/PSJC/Services/911/911dispatch/calldatachema.php#}InNum').text}
                #create a list of dictionaries
                listings.append(listing)
        return listings        
    
    def format_datetime(self, date):
	    # convert date and time format from CST to UTC
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
		self.tm_obj = Sthundermaps.ThunderMaps(key)
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
		
			# Wait 15 minutes before trying again.
			time.sleep(60 * 15)
			
updater = Updater(key, account_id)
updater.start()