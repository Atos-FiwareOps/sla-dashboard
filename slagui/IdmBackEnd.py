__author__ = 'root'

'''
Created on 30/06/2014

@author: s270094
'''
from django.conf import settings
from django.contrib.auth.models import User
import requests
import urlparse
import json

class IdmBackEnd(object):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name, and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051de'
    """
    def authenticate(self, token=None):
        token_valid = self.validateToken(token)
        if token_valid:
            try:
                userJson = self.getUserInformation(token)
                roles = []
                #for item in userJson["roles"]:
                 #   roles.append(item["name"])

                user = User.objects.get(username= userJson['id'])
                user.email = userJson["email"]
                org_list = userJson["organizations"]
                user.organizations = []
                for org in org_list:
                    if org['roles']:
                        user.organizations.append(org)
                user.roles = []
                for role in userJson["roles"]:
                    user.roles.append(role["name"])
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; the password
                # from settings.py will.
                user = User(username= userJson['id'])
                user.set_unusable_password()
                user.is_staff = False

                user.is_superuser = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def getUserInformation(self, token):
        print '//////////////Token///////////////'
        print token['access_token']
        print token['refresh_token']
        print token['token_type']
        print token['expires_in']
        http = settings.IDM_HTTP_TYPE
        host = settings.IDM_URL
        path = '/user'
        params = { 'access_token': token['access_token']}
        query = urlparse.urlunparse((http,host,path, '', paramunparse(params), ''))
        print query

        result = requests.get(query)
        print "GET {} {} {}".format(result.url, result.status_code, result.text[0:500])

        json_user = json.loads(result.text)
        return json_user

    def validateToken(self, token):
        '''It is responsible to valide the token'''
        '''TODO increase the validation, expired time....'''
        try:
            if token['access_token'] is None:
                return False
        except:
            return False
        return True

''' TODO share the method in Util '''
def paramunparse(params):
    result = ""
    for k, v in params.iteritems():
        result += k + "=" + v + "&"
    return result.rstrip('&')

