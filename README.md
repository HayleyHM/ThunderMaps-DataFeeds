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

### Feed module

To use the Portland 911 Dispatch module, import it into your code using `import portland_dispatch_feed` and create an instance of the `Dispatch` class.

To get listings from the feed, use the `format_feed()` method:

```python
import portland_dispatch_feed

# Get listings from Portland Dispatch
list_feed = portland_dispatch_feed.Dispatch()
listings = list_feed.format_feed()
```

Each feed.py module should be relatively similar when pulling from an RSS feed although the formatting of the subheadings may vary. This module will return a list of dictionaries ready to be posted to ThunderMaps.

### ThunderMaps module

To use the ThunderMaps module by [DanielGibbsNZ](https://github.com/DanielGibbsNZ/thundermaps-trademe), import it into your code using `import thundermaps` and create an instance of the ThunderMaps class using your ThunderMaps API key.

```python
import thundermaps

# Replace ... with the actual values.
THUNDERMAPS_API_KEY = "..."
ACCOUNT_ID = ...

# Get reports for an account.
my_thundermaps = thundermaps.ThunderMaps(THUNDERMAPS_API_KEY)
reports = thundermaps.getReports(ACCOUNT_ID)
```

### Updater module

The updater module combines both the Feed and ThunderMaps modules and provides a higher level interface for generating ThunderMaps reports for the latest listings. Using the updater module typically consists of these steps:

1. Creating a new instance of Updater with a ThunderMaps API key
2. Adding categories to generate reports for
3. Starting the updater

For Example:

```python
import updater

# Define categories, keys and accounts here
THUNDERMAPS_API_KEY = ''
THUNDERMAPS_ACCOUNT_ID = ''
THUNDERMAPS_CATEGORY_ID = ''

# Create updater
feed_updater = updater.Updater(THUNDERMAPS_API_KEY, THUNDERMAPS_ACCOUNT_ID, THUNDERMAPS_CATEGORY_ID)

#Start updating
feed_updater.start()
```
  
__Important:__ The updater module uses `.source_ids_` files to store the id's of listings which have already been posted. If you delete these files then it will post duplicates.

Current Usage
=============

These modules are currently used all [ThunderBot](http://www.thundermaps.com/users/1109) accounts, including:
* Drone Strikes
* Portland 911 Dispatch
* NATO Piracy
* Worldwide Earthquakes
* UK Traffic 
* and many more...
