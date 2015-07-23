__author__ = 'root'

import json
import socket
import urllib2
import sys

from django.conf import settings


class MarketplaceAdapter(object):


	__instance = None
	__timeout_value = 4

	org_node_list = {
		'TRENTO':'Trento',
		'LannionNode': 'Lannion2'
	}

	def __new__(cls):
		if cls.__instance is None:
			print("NEW SINGLETON")
			cls.__instance = object.__new__(cls)
			cls.__instance.name = "Marketplace Adapter Singleton.."
		else:
			print("Marketplace SINGLETON EXISTS")
		return cls.__instance


	def do_marketplace_request(self, request_url):
		"""Execute the request to the url.
			*GET request if there isn't data parameter

		Keyword arguments:
		request_url -- URL to call
		"""
		resp = None
		print("INFO do_marketplace_request:")

		opener = urllib2.build_opener()
		try:
			print("URL= " + request_url)

			request = urllib2.Request(request_url)
			response = opener.open(request, timeout=self.__timeout_value)
			if response.code != 200:
				print("Response.code=%d" % response.code)
				raise Exception('Error occurred while connecting to Marketplace - Response code: ' + str(response.code))
			else:
				resp = response.read()

				return json.loads(resp)

		except urllib2.HTTPError, e:
			print("urllib2.HTTPError: url={} code={} msg={}".format(e.url, e.code, e.msg))
			raise Exception('Error occurred while connecting Marketplace - HttpError - ' + str(e.msg))
		except urllib2.URLError, e:
			print("urllib2.URLError: msg={}".format(e.message))
			raise Exception('Error occurred while connecting Marketplace - UrlError - ' +str(e.reason))
		except socket.timeout:
			print("socket.timeout: request timeout!")
			raise Exception('Error occurred while connecting Marketplace - Socket Timeout')
		except:
			print(sys.exc_info()[0])
			raise Exception('Error occurred while connecting Marketplace')
