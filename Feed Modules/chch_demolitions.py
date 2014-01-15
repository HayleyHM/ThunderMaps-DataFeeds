import urllib.request
import time
import uuid

demolitions_file = urllib.request.urlretrieve("http://cera.govt.nz/demolitions/xml", 'demolitions_feed.xml')

import xml.etree.ElementTree as ET
tree = ET.parse('demolitions_feed.xml')
root = tree.getroot()

class Christchurch_Demolitions:
     
          def format_feed(self):
                    listings = {}
                    for building in tree.iter(tag='node'):
                              demolition_id = building[0].text
                              unique_id = str(uuid.uuid1())
                              description = ("Building:", building[0].text, "Demolition status:", building[2].text, "Heritage status:", building[3].text)
                              latitude = building[4].text
                              longitude = building[5].text
                                                            
                              listings[demolition_id] = [unique_id, description, latitude, longitude]

                    return listings