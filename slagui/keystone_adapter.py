# -*- coding: utf-8 -*-
__author__ = 'root'

import json
import socket
import urllib2
import sys
from django.conf import settings
import unicodedata

class KeyStoneAdapter(object):
    
    #This values have been moved to the setting configuration.
    #URL_KEYSTONE = "http://cloud.lab.fi-ware.org:4730"
    #URL_TOKEN = "/v3/auth/tokens"
    #URL_USER = "/v3/users/"
    #BODY_KEYSTONE = "{\"auth\": {\"identity\": { \"methods\": [ \"oauth2\" ], \"oauth2\": {\"access_token_id\":\"ACCESS_TOKEN_VALUE\"}}}}"
    __timeout_value = 4
    
    
    def __init__(self):
        pass
    
    def get_actorId(self, token, userId): 
        """Find the ActorId through the KeyStone IdM that is associated to the tenantId project in the OpenStack.
 
        Keyword arguments:
            token -- AUTH2 token to obtain the actorId for the cloud organization.
            userId -- user identification included in the AUTH2 authentication
        
        Exception
            The method manage all the exception (printing the error by console) and arise the exception to be managed.
        """
        #Obtain the token for the KeyStone IdM
        _url_token = settings.CLOUD_URL_KEYSTONE + settings.CLOUD_URL_TOKEN
        _body = settings.CLOUD_BODY_KEYSTONE.replace("ACCESS_TOKEN_VALUE", token)
        _headers = {'content-type': 'application/json'}
        tokenKeyStone = self.call_keyStoneIdM(_url_token, _headers, _body, True)

        #Obtain the associated user information.
        _url_user = settings.CLOUD_URL_KEYSTONE + settings.CLOUD_URL_USER + userId
        _body_user = None
        _headers_user = {'X-Auth-Token': tokenKeyStone}
        
        actorId = self.call_keyStoneIdM(_url_user, _headers_user, _body_user, False)
        return actorId

    def call_keyStoneIdM(self, url, headers, body=None, returnTokenKeyStone=False): 
        """Execute the request to the url. The method allows to obtain the Token of the header (without to collect the response) 
           and, also, the message of the call.
            *POST request if there is body parameter
            *GET request if there isn't body parameter

        Keyword arguments:
        request_url -- URL to call
        data -- data to be included in the POST request
        returnTokenKeyStone -- Indicates if the method only return the Token of the header without to collect the return message.
        """
              
        opener = urllib2.build_opener()
        try:
            print("URL keystone= " + url)
            if body == None:
                method = "GET"
            else:
                method = "POST"
            print("KeyStoneIDM: Request {} : {} ".format(method, url))
 
            request = urllib2.Request(url, body, headers)

            response = opener.open(request, timeout=self.__timeout_value)
            if response.code in [200, 201]:
                if returnTokenKeyStone:
                    return response.info().getheader('X-Subject-Token')
                    
                else:
                    resp = response.read()
                    user_resp = json.loads(resp)
                    actorId =user_resp["user"]["cloud_project_id"]
                    print ("KeyStoneIDM: the ActorId value is: " + actorId)
                    return actorId
                    
            else:
                print("KeyStoneIDM: Response.code=%d" % response.code)
                raise Exception('Error occurred while connecting to Keystone IdM - Response code: ' + str(response.code))                

        except urllib2.HTTPError, e:
            print("urllib2.HTTPError: url={} code={} msg={}".format(e.url, e.code, e.msg))
            raise Exception('Error occurred while connecting KyeStone IdM - HttpError - ' + str(e.msg))
        except urllib2.URLError, e:
            print("urllib2.URLError: msg={}".format(e.msg))
            raise Exception('Error occurred while connecting Keystone IdM - UrlError - ' +str(e.reason))
        except socket.timeout:
            print("socket.timeout: request timeout!")
            raise Exception('Error occurred while connecting Keystone IdM - Socket Timeout')
        except:
            print(sys.exc_info()[0])
            raise Exception('Error occurred while connecting Keystone IdM')
   
    
if __name__ == '__main__':
    #actorId = KeyStoneAdapter().get_actorId("ysxaa9an31aA1EgtFe909UJcE6LVh7", "quim")
    
    #print actorId
    error = "Error PaaS: Error occurred while connecting FM - UrlError - [Errno 10061] No se puede establecer una conexi�n ya que el equipo de destino deneg� expresamente dicha conexi�n"
    print "test " + error.decode('utf-8', 'ignore')


    
 
    