ThunderMaps-DataFeeds
=====================
This repository provides Python modules for using RSS feeds and API documentation to get data listings and using the ThunderMaps API to post reports, and an updater module which creates new ThunderMaps reports for the latest listings.

Dependencies
------------

* The `requests` library for Python 3
* A ThunderMaps API key and Account ID
* (Optional) The `pytz` library for timezone formatting

Usage
-----

### Combined module

The Combined module is a module which has combined the previous feed.py and updater.py modules. This combined module provides a higher level interface for generating ThunderMaps reports for the latest listings. 

To use the combined_example module simply adjust the formatting found under `self.feed_obj.format_feed()` to suit your input feed. Enter your key and account variables as below...

```python
key = '<THUNDERMAPS_API_KEY>'
account_id '<THUNDERMAPS_ACCOUNT_ID>'
```

Note: Each combined_feed.py module should be relatively similar when pulling from an RSS feed although the formatting of the subheadings may vary. This module will return a list of dictionaries ready to be posted to ThunderMaps.

__Important:__ The updater module uses `.source_ids_` files to store the id's of listings which have already been posted. If you delete these files then it will post duplicates.

### ThunderMaps module

To use the ThunderMaps module by [DanielGibbsNZ](https://github.com/DanielGibbsNZ/thundermaps-trademe), import it into your code first by altering the directory to your Pthundermaps.py file. The `Pthundermaps.py` module includes the photo upload capabilities which are not present on the original thundermaps.py file. 

```python
import sys
sys.path.append(r'/usr/local/thundermaps') #Grabs the Pthundermaps.py location for import
import Pthundermaps #thundermaps.py file with photo upload capabilities
```


Current Usage
=============

These modules are currently used by [ThunderBot](http://www.thundermaps.com/users/1109) accounts, including:
* USGS Landsat 7 Satellite Imagery
* USGS Landsat 8 Satellite Imagery
* GeoStock Global Photos
* and many more...
