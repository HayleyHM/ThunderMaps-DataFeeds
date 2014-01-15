'''strikes.py - This program is used to retrieve and manage an API supplied by joshbegley of Real time and Historical United States Drone Strikes. To use this you must have an API key from Mashape.com

Author: Hayley Hume-Merry
Date: 18/12/2013'''

import requests
import json


class DroneStrikes:
    def format_feed(self): 
        '''Retrieves the API from mashape using the mashape api key'''
        drone_feed = requests.get("https://joshbegley-dronestream.p.mashape.com/data", headers={"X-Mashape-Authorization": "V3NlU4y6UqdqxziDunLvSChYZkjAhM0r"})
        listings = []
        drone_strikes = drone_feed.json()
        for strike in drone_strikes["strike"]:
            listing = {"occurred_on":strike["date"].replace('T', ' ').replace('.000Z', ''), 
                      "latitude":strike["lat"], 
                      "longitude":strike["lon"], 
                      "description":strike["bij_summary_short"],
                      "category_name":(strike["country"] + " - Drone Strike Reported"),
                      "source_id":strike["_id"]
                }
            listings.append(listing)
        return listings