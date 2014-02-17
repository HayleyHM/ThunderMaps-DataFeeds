#
#global_alerts.py
#Module for pushing Global Alert updates from Global Disaster Alert and Coordinate System website. <http://www.gdacs.org/> Also pushes updates to ThunderMaps.com
#Author: Hayley Hume-Merry <hayley@thundermaps.com>
#

import urllib.request
import time
import pytz, datetime
import xml.etree.ElementTree as ET
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'  
account_id = 'gdacs-alerts'


class Incidents:
    def format_feed(self):
        #Retrieves the data feed and stores it as xml
        demolitions_file = urllib.request.urlretrieve('http://www.gdacs.org/XML/RSS.xml', 'global_incidents.xml')
        tree = ET.parse('global_incidents.xml')
        listings = []
        for item in tree.iter(tag='item'):
            alert_title = item[0].text
            unique_id = item[3].text.split('=')
            incident_type = item[12].text
            date_time = item[4].text
            format_date = self.format_datetime(date_time)
            if 'earthquake' in item.find('title').text.lower():
                primary_category = 'Earthquake'
            elif 'cyclone' in item.find('title').text.lower():
                primary_category = 'Cyclone'
            elif 'tsunami' in item.find('title').text.lower():
                primary_category = 'Tsunami'
            elif 'tornado' in item.find('title').text.lower():
                primary_category = 'Tornado'
            elif 'storm' in item.find('title').text.lower():
                primary_category = 'Storm'
            elif 'eruption' in item.find('title').text.lower():
                primary_category = 'Volcanic Eruption'
            elif 'flood' in item.find('title').text.lower():
                primary_category = 'Flood'
            else:
                primary_category = 'Global Disaster Alert'
            #format each parameter into json format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":item[9][0].text, 
                       "longitude":item[9][1].text, 
                       "description":alert_title + '<br/>' + item[1].text,
                       "category_name":primary_category,
                       "source_id":unique_id[-1]}
            #create a list of dictionaries
            listings.append(listing)            
        return listings
    
    
    def incident(self, incident_type):
        #Redefine the event incident type for users
        event = {'FL':'Flood', 'EQ':'Earthquake', 'TC':'Tropical Cyclone'}
        if incident_type in event.keys():
            event_type = event[incident_type]
        else:
            event_type = "Incident Alert"
        return event_type
            
    def format_datetime(self, date_time):
        #convert date and time format from GMT to UTC
            date_time = date_time.strip(' GMT').split()
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            if date_time[2] in monthDict:
                month = monthDict[date_time[2]]
            date_time = str(date_time[3]) + '-' + str(month) + '-' + str(date_time[1]) + ' ' + date_time[4]
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
		
			# Wait 20 minutes before trying again.
			time.sleep(60 * 20)
			
updater = Updater(key, account_id)
updater.start()