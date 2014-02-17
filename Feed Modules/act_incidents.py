#
#incidents.py
#Module for pushing new Australian Captial Territory Incident updates through to users on ThunderMaps.com
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import pytz, datetime
import time
import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps' 
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'act-current-incidents'

class Incidents:    
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        incidents = urllib.request.urlretrieve('http://esa.act.gov.au/feeds/currentincidents.xml', 'incident_feed.xml')
        tree = ET.parse('incident_feed.xml')
        listings = []
        for item in tree.iter(tag='item'):
                incident_name = item[0].text
                unique_id = item[3].text
                date_time = item[4].text
                date = self.format_datetime(date_time)
                location = item[5].text.split()
                summary = item.find('description').text.split('<br />')
                agency = summary[5].replace('Agency: ', '')
                incident_type = summary[4].replace('Type: ', '')
                if 'fire' in incident_type.lower():
                        primary_category = 'Fire'
                elif 'vehicle accident' in incident_type.lower():
                        primary_category = incident_type.title()
                elif 'medical' in incident_type.lower():
                        primary_category = 'Medical'
                else:
                        primary_category = 'General Duties'
                #format each parameter into json format for application use
                listing = {"occurred_on":date, 
                           "latitude":location[0], 
                           "longitude":location[1], 
                           "description":item.find('description').text.title().replace('<Br />', '<br/>'),
                           "primary_category_name": primary_category,
                           "secondary_category_name": agency,
                           "source_id":item.find('guid').text
                       }
                #create a list of dictionaries
                listings.append(listing)            
        return listings
                
           
    def format_datetime(self, date_time):
        #convert date and time format from AEST to UTC
        date_time = date_time.strip('EST').split()
        day = date_time[0]
        monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        month = date_time[1]
        if month in monthDict:
            month = monthDict[month]
        year = date_time[2]
        date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[3])
        
        local = pytz.timezone("Australia/Victoria")
        naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst = None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = str(utc_dt)
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