'''This module can be used to retrieve New Zealand upcoming events. The data is drawn from <www.eventfinda.co.nz>

Author: Hayley Hume-Merry
Date: 7/01/2014'''

import requests
import json
import pytz, datetime

class Events:
    def format_feed(self):
        listings = []
        #Retrieves and formats the event data from EventFinda's API ... Authentication is required
        authentication = ('<username>', '<password>')
        headers={
            "X-Mashape-Authorization": "<Mashape_Auth>"
          }    
        event_feed = requests.get("https://eventfinda-eventfinda-nz.p.mashape.com/events.json", auth=authentication, headers=headers)
        event_info = event_feed.json()
        for event in event_info['events']:
            #Formats the required data into reports
            location = event['point']
            latitude = location['lat']
            longitude = location['lng']
            date = event['datetime_start']
            format_date = self.format_datetime(date)
            event_url = '<a href=' + str(event['url']) + '>here</a>'
            if event['is_free'] == False:
                price = 'Click %s for price information.' % event_url
            else:
                price = 'Free Entry.'
            description = event['name'].upper() + '\n' + 'Entry Restrictions: '+ event['restrictions'] + '\n' + price + '\n' + event['description']
            event_id = event['id']
            event_type = event['category']
            event_type = event_type['name']
            #Converts the data into JSON format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":event_type,
                       "source_id":event_id,}
            listings.append(listing)
        return listings
                
    def format_datetime(self, date):
                #convert date and time format from GMT to UTC
                local = pytz.timezone("GMT")
                naive = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                local_dt = local.localize(naive, is_dst = None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = str(utc_dt)
                return utc_dt