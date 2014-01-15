'''This module can be used to retrieve and format GeostockPhoto Data for application use.

Author: Hayley Hume-Merry
Date: 07 January 2014'''

import requests
import json
import pytz, datetime

class GeoStock:
    def format_feed(self):
        listings = []
        #Returns photo_id's of available photos
        photo_ids = self.get_photo_ids()
        for i in photo_ids:
            #Returns photo information for each individual photo_id
            photo_params = {"id":i}
            photo_feed = requests.get('http://geostockphoto.com/photo/getInfo/apiKey/<api_key>', params=photo_params)
            try:
                info = photo_feed.json()
            except ValueError:
                continue
            else:
                pass
            #Formats the photo information
            latitude = info['lat']
            longitude = info['lng']
            date = info['approvedDate']
            format_date = self.format_datetime(date)
            description = info['title']
            rank_id = info['rate']
            rank_id = "GeoStock Photo" + (" - Rank %s" %rank_id)
            photo_id = i
            #Converts the data into JSON format for application use
            listing = {"occurred_on":format_date, 
                       "latitude":latitude, 
                       "longitude":longitude, 
                       "description":description,
                       "category_name":rank_id,
                       "source_id":photo_id,
                }
            listings.append(listing)
        return listings    
    
        
    def get_photo_ids(self):
        #Uses a wide search to collect photo_ids of available photos
        photo_ids = []
        search_params = {"thumb":"430"}
        search_feed = requests.get('http://geostockphoto.com/photo/getSearch/apiKey/<api_key>', params=search_params)
        all_photos = search_feed.json()
        for photo in all_photos["photo"]:
            photo_id = photo["id"]
            photo_ids.append(photo_id)
        return photo_ids
    
    
    def format_datetime(self, date):
            #convert date and time format from GMT to UTC
            date_time = date.replace('/', ' ').split()
            day = date_time[0]
            monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            month = date_time[1]
            if month in monthDict:
                month = monthDict[month]
            year = date_time[2]
            date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[4])
            
            local = pytz.timezone("GMT")
            naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            local_dt = local.localize(naive, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = str(utc_dt)
            return utc_dt
