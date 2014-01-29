#
# thundermaps.py
#
# Module for interacting with the Thundermaps API.
# To use this you must have registered a Thundermaps and known your API key and account ID.
#
# Author: Daniel Gibbs <danielgibbs.name>
#

import requests
import json
import time

class ThunderMaps:
	# Which server to use. "www" is the production server, "staging" is the staging server.
	server = "www"

	# Create a new ThunderMaps instance with the API key.
	def __init__(self, key):
		self.key = key

	# Set whether to use the staging server.
	def staging(self, on=True):
		self.server = "staging" if on else "www"

	# Send a list of reports to ThunderMaps.
	def sendReports(self, account_id, reports):
		try:
			data = json.dumps({"reports": reports})
			url = "http://%s.thundermaps.com/api/reports/" % self.server
			params = {"account_id": account_id, "key": self.key}
			headers = {"Content-Type": "application/json"}
			resp = requests.post(url, params=params, data=data, headers=headers)
			return resp
		except Exception as e:
			print ("[%s] Error creating reports: %s" % (time.strftime("%c"), e))
			return None

	# Get a list of reports from ThunderMaps.
	def getReports(self, account_id):
		try:
			page = 1
			more = True
			result = []
			while more:
				url = "http://%s.thundermaps.com/api/reports/" % self.server
				params = {"account_id": account_id, "key": self.key, "page": page}
				print ("url=%s params=%s" % (url, params))
				resp = requests.get(url, params=params)
				r = resp.json()
				if len(r) == 0:
					more = False
				else:
					result.extend(r)
					page = page + 1
			return result
		except Exception as e:
			print ("[%s] Error getting reports: %s" % (time.strftime("%c"), e))
			return None

	# Delete a specific report from ThunderMaps.
	def deleteReport(self, report_id):
		try:
			url = "http://%s.thundermaps.com/api/reports/%d/" % (self.server, report_id)
			params = {"key": self.key}
			resp = requests.delete(url, params=params)
			return resp
		except Exception as e:
			print ("[%s] Error deleting report: %s" % (time.strftime("%c"), id, e))
			return None

	# Upload an image to ThunderMaps and return the attachment ID.
	def uploadImage(self, image_url):
		try:
			data = json.dumps({"attachment": {"attachment": image_url, "from_url": True, "type": "ReportImage"}})
			url = "http://%s.thundermaps.com/api/attachments/" % self.server
			params = {"key": self.key}
			headers = {"Content-Type": "application/json"}
			resp = requests.post(url, params=params, data=data, headers=headers)
			return resp.json()["id"]
		except Exception as e:
			print ("[%s] Error uploading image: %s" % (time.strftime("%c"), e))
			return None
