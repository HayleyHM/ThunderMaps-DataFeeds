#
#fire_html.py
#Module which scrapes the NZ Fire Service Alert Pages - Also pushes updates to ThunderMaps.com
#
#Author: Hayley Hume-Merry <hayley.ahm@gmail.com>
#

import re
import time
import pytz, datetime
import urllib.request
from bs4 import BeautifulSoup
from geopy import geocoders
import sys
sys.path.append(r'/usr/local/thundermaps') #r'C:\Users\H\Documents\Jobs\ThunderMaps\Data Feeds\ThunderMaps'
import Wthundermaps

key = 'THUNDERMAPS_API_KEY'
account_id = 'nz-fire-incidents'

class Incidents:
    def format_feed(self):
        listings = []
        region = ['Nth', 'Cen', 'Sth']
        for i in region:
            url_date = self.date()
            url_link = str(i) + str(url_date)
            url = 'http://incidents.fire.org.nz/%s.html' % url_link
            filehandle = urllib.request.urlopen(url)
            soup = BeautifulSoup(filehandle.read())
            soup_reports = soup('table', {'width' : '100%'})[3:-1]
            for j in soup_reports:
                address = re.sub('<[^>]*>', '', str(j('span', {'class':'Address'})))
                address = ''.join(address).replace('[', '').replace(']', '').strip()
                if 'UNKN' in address:
                    geocode_address = address.split(' ', 1)[1]
                elif 'and' in address:
                    geocode_address = address.split('and', 1)[1]
                else:
                    geocode_address = address
                location = self.geocoder(geocode_address)
                if location == None:
                    pass
                else:
                    pub_date = str(j.td)
                    time_recorded = re.sub('<[^>]*>', '', pub_date).split()[3]
                    occurred = self.format_datetime(time_recorded)
                    summary = j('td', {'class':'TableData'})[1:]
                    duration = re.sub('<[^>]*>', '', str(summary[0])).strip()
                    station = re.sub('<[^>]*>', '', str(summary[1])).strip().title()
                    incident_title = re.sub('<[^>]*>', '', str(summary[-1])).strip()
                    category = incident_title.replace(')', '').split('(')
                    if 'stru' in category[-1].strip().lower():
                        primary_category = 'Structural'
                    elif 'sprnklr' in category[-1].strip().lower():
                        primary_category = 'Sprinkler'
                    elif 'resc' in category[-1].strip().lower():
                        primary_category = 'Rescue'
                    elif 'med' in category[-1].strip().lower():
                        primary_category = 'Medical'
                    else:
                        primary_category = 'General Duties'
                    # complies information into json format for application use
                    listing = {"occurred_on":occurred,
                               "latitude":location[0], 
                               "longitude":location[1], 
                               "description":incident_title[5:].title() + '<br/>' + 'Station: ' + station + '<br/>' + 'Duration: ' + duration,
                               "primary_category_name":primary_category,
                               "source_id":j.td.b.string}
                    #create a list of dictionaries
                    listings.append(listing)
                time.sleep(3)
        return listings
    
    def date(self):
        year = str(time.localtime().tm_year)
        month = str(time.localtime().tm_mon)
        if len(month) == 1:
            month = '0' + month
        day = str(time.localtime().tm_mday)
        date = year + month + day
        return date
    
    def format_datetime(self, time_recorded):
        date_time = str(time.localtime().tm_year) + '-' + str(time.localtime().tm_mon) + '-' + str(time.localtime().tm_mday) + ' ' + time_recorded
        local = pytz.timezone("NZ")
        naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst = None)
        utc_dt = str(local_dt.astimezone(pytz.utc))
        return utc_dt    
    
    def geocoder(self, geocode_address):
        #Geocodes addresses using the GoogleV3 package. This converts addresses to lat/long pairs
        try:
            g = geocoders.GoogleV3()
            (street, (lat, long)) = g.geocode(geocode_address)
            if (lat, long) == 'None':
                pass
            else:
                return (lat, long)
        except TypeError:
            pass
        
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