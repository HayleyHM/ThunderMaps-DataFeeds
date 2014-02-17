#
#This module can be used to retrieve live Queensland, Australia Fire Service Data and update for the ThunderMaps Application.
#
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#Date: 23 December 2013'''
#
import urllib.request
import time
import xml.etree.ElementTree as ET
import pytz, datetime
import time
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps' 
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'qld-rural-fire-incidents'

class Incidents:
    def format_feed(self):
        #Retrieves and formats the piracy data from NATO's RSS Feed
        feed_file = urllib.request.urlretrieve('https://ruralfire.qld.gov.au/bushfirealert/bushfireAlert.xml', 'qld_fires.xml')
        tree = ET.parse('qld_fires.xml')
        listings = []
        for alert in tree.iter(tag='item'):
            #Extracts the data from a number of subheadings within the feed
            location = alert[6].text.split()
            date = alert.find('pubDate').text
            format_date = self.format_datetime(date)
            #Converts the data into JSON format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":location[0], 
                       "longitude":location[1], 
                       "description":alert.find('description').text.replace('<br />', '<br/>'),
                       "category_name":alert.find('author').text,
                       "source_id":alert.find('title').text
                }
            listings.append(listing)
        return listings        
    
    def format_datetime(self, date):
            #Re-formats the publish time/date into UTC format
                date_time = date.split()
                monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                if date_time[2] in monthDict:
                    month = monthDict[date_time[2]]
                date_time = str(date_time[3]) + '-' + str(month) + '-' + str(date_time[1]) + ' ' + str(date_time[4])
                local = pytz.timezone("Australia/Queensland")
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
		
			# Wait 20 minutes before trying again.
			time.sleep(60 * 20)
			
updater = Updater(key, account_id)
updater.start()