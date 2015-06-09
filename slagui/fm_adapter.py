__author__ = 'root'

import json
import socket
import urllib2

#import time

from django.conf import settings

import sys
import base64

class FMAdapter(object):
    
    DCA = "DCA"
    FM = "FM"
    TOKEN_DCA = "TOKEN_DCA"
    TOKEN_FM = "TOKEN_FM"
    __instance = None
    __token_dca = None
    __token_fm = None
    __timeout_value = 4

    #credentials to obtain the token



    org_node_list = {
        'TRENTO':'Trento',
        'LannionNode': 'Lannion2'
    }
    #http://130.206.84.4:1028/monitoring/regions/Trento/hosts
    dca_request_url = settings.DCA_NODE_URL

    def __new__(cls):
        if cls.__instance is None:
            print("NEW SINGLETONE")
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "FM Adapter Singleton.."
            cls.__instance.get_tokens()
        else:
            print("SINGLETONE EXISTS")
        return cls.__instance

    def get_tokens(self):
        #isExpired = lambda timestamp: timestamp if time.time() <= timestamp else None

        print("recover TOKEN")

        # Recover from cache, if exists
        print("Looking for the token in cache")

        request_url = settings.CLOUD_TOKEN_URL
        #credentials = settings.DCA_GATHER_USER['credentials']
        tokenComponent = [self.TOKEN_DCA, self.TOKEN_FM]
        for i in tokenComponent:
            data_token = self.do_fm_request( request_url, settings.DCA_GATHER_USER, True, i)
            try:
                print("Saved token in cache")
                print("Token: id={} expire={}".format(data_token['access_token'], data_token['expires_in']))
                token = data_token['access_token']
                if i == self.TOKEN_DCA:
                    self.__token_dca = token
                else:
                    self.__token_fm = token
            except Exception as e:
                print('Token retrieve ERROR:' + str(e) + 'in the message: ' + str(data_token) + 'for the component '+ i)
                self.__token = ''

        # Execute a generic DCA interrogation


    def do_fm_request(self, request_url, data=None, is_host_request=False, host_name=None):
        """Execute the request to the url. 
            *POST request if there is data parameter
            *GET request if there isn't data parameter

        Keyword arguments:
        request_url -- URL to call
        data -- data to be included in the POST request
        is_host_request -- Indicates if a header with the token need to be included in the request
        host_name -- Indicates the name of the component/host: DCA, FM and Token
        """
        responseDCA = None
        print("INFO do_fm_request:")
        #Method used depending on the data content
        if data == None:
            method = "GET"
        else:
            method = "POST"
        print("Request {} : {}".format(method, request_url))

        headers = {'content-type': settings.JSON_HEADER, 'accept': settings.JSON_HEADER}
        if is_host_request:
            #identify the type of host, since the header is different.
            # When the application will use only one token, it have to be simplify. 
            if ((host_name == self.TOKEN_DCA) | (host_name == self.TOKEN_FM)):
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                encodeAuth = None
                if host_name == self.TOKEN_DCA:
                    encodeAuth = base64.b64encode(settings.SECRET_TOKEN_DCA + ':' + settings.SECRET_KEY_DCA)
                else:
                    encodeAuth = base64.b64encode(settings.SECRET_TOKEN_FM + ':' + settings.SECRET_KEY_FM) 
                headers['Authorization'] = 'Basic ' + encodeAuth 
            
            else:
                headers = {'content-type': settings.JSON_HEADER, 'accept': settings.JSON_HEADER}
                if host_name == self.DCA:
                    headers['X-Auth-Token'] = self.__token_dca
                elif host_name == self.FM:
                    headers = {'content-type': settings.JSON_HEADER, 'accept': settings.JSON_HEADER}
                    headers['Authorization'] = 'Bearer ' + base64.b64encode(self.__token_fm)
                else:
                    headers = {'content-type': settings.JSON_HEADER, 'accept': settings.JSON_HEADER}
                    headers['X-Auth-Token'] = self.__token_dca

        opener = urllib2.build_opener()
        try:
            print("Tokens= Dca:" + str(self.__token_dca)+", FM"+ str(self.__token_fm) )
            print("URL= " + request_url)
            print("METHOD= " + method)
            print("HEADERS= " + str(headers))
            print("DATA= " + str(data))

            request = urllib2.Request(request_url, data, headers)
            response = opener.open(request, timeout = self.__timeout_value)
            if response.code != 200:
                print("Response.code=%d" % response.code)
                raise Exception('Error occured while connecting to FM - Response code: ' + str(response.code))
            else:
                responseDCA = response.read()

                return json.loads(responseDCA)

        except urllib2.HTTPError, e:
            print("urllib2.HTTPError: url={} code={} msg={}".format(e.url, e.code, e.msg))
            raise Exception('Error occurred while connecting ' + host_name + ' - HttpError - ' + str(e.msg))
        except urllib2.URLError, e:
            print("urllib2.URLError: msg={}".format(e.message))
            raise Exception('Error occurred while connecting ' + host_name + ' - UrlError - ' +str(e.reason))
        except socket.timeout:
            print("socket.timeout: request timeout!")
            raise Exception('Error occurred while connecting ' + host_name + 'Socket Timeout')
        except:
            print(sys.exc_info()[0])
            raise Exception('Error occurred while connecting ' + host_name)
