import urllib.request
import pytz, datetime
import xml.etree.ElementTree as ET

class Incidents:
    def format_feed(self):
        traffic_feed = urllib.request.urlretrieve('http://www.trafficscotland.org/rss/feeds/currentincidents.aspx', 'incident_feed.xml')
        tree = ET.parse('incident_feed.xml')
        listings = []
        for item in tree.iter(tag='item'):
            unique_id = item.find('link').text.split('/')
            date = item.find('pubDate').text
            format_date = self.format_datetime(date)
            location = item[3].text.split()
            incident_type = item.find('title').text.split(' - ')
            #format each parameter into a dictionary
            listing = {"occurred_on":format_date, 
                        "latitude":location[0], 
                        "longitude":location[1], 
                        "description":item.find('description').text.replace('<p>', '').replace('</p>', ''),
                        "category_name":incident_type[1],
                        "source_id": unique_id[3]}
            #create a list of dictionaries
            listings.append(listing)
        return listings
    
    def format_datetime(self, date):
                #convert date and time format from GMT to UTC
                date_time = date.split()
                day = date_time[1]
                monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                month = date_time[2]
                if month in monthDict:
                    month = monthDict[month]
                year = date_time[3]
                date_time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(date_time[4])
                
                local = pytz.timezone("GMT")
                naive = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                local_dt = local.localize(naive, is_dst = None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = str(utc_dt)
                return utc_dt