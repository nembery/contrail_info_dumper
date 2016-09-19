#!/usr/bin/env python
# simple script to dump various items from a contrail cluster
# nembery@juniper.net 02-08-16

import json
import urllib2
import sys
import getpass


class ContrailRestClient:
    _user = ''
    _pw = ''
    _host = ''
    _auth_url = ":5000/v3/auth/tokens"

    _auth_token = ""

    def __init__(self, user, pw, host):
        self._user = user
        self._pw = pw
        self._host = host

    def connect(self):

        _auth_json = """
            { "auth": {
                "identity": {
                  "methods": ["password"],
                  "password": {
                    "user": {
                      "name": "%s",
                      "domain": { "id": "default" },
                      "password": "%s"
                    }
                  }
                },
                  "scope": {
                        "project": {
                            "domain": {
                                "id": "default"
                            },
                            "name": "admin"
                        }
                    }
                }
            }
            """ % (self._user, self._pw)

        request = urllib2.Request("http://" + self._host + self._auth_url)
        request.add_header("Content-Type", "application/json")
        request.add_header("charset", "UTF-8")
        request.add_header("Content-Length", len(_auth_json))
        result = urllib2.urlopen(request, _auth_json)
        self._auth_token = result.info().getheader('X-Subject-Token')
        return True

    def perform_get(self, url):
        if url.startswith('/'):
            # if this relative url, let's construct the full url
            url = "http://" + self._host + ":8082" + url

        request = urllib2.Request(url)
        request.add_header("Content-Type", "application/json")
        request.add_header("charset", "UTF-8")
        request.add_header("X-Auth-Token", self._auth_token)
        request.get_method = lambda: 'GET'
        result = urllib2.urlopen(request).read()

        json_string = json.loads(result)
        return json.dumps(json_string, indent=2)


if __name__ == '__main__':
    print "Contrail Information Utility"
    # prompt for authentication credentials
    host = raw_input("Enter your Contrail Cluster IP: ")
    username = raw_input("Enter your Contrail Cluster Username: ")
    password = getpass.getpass("Enter your Contrail Cluster Password: ")

    # instantiate our rest client
    crc = ContrailRestClient(username, password, host)
    if not crc.connect():
        print "Could not connect to Cluster!!!"
        sys.exit(1)

    # these are the things we are going to recursively dump out
    desired_urls = ['/projects', '/virtual-networks', '/network-policys', '/service-instances',
                    '/floating-ip-pools', '/floating-ips', '/route-tables'
                    ]

    # iterate over each of the desired_urls
    for url in desired_urls:
        print "Performing GET on URL: %s" % url
        o = crc.perform_get(url)
        j = json.loads(o)
        print "============"
        # now, replace the beginning / if it exists
        for child in j[url.replace('/', '')]:
            print "==="
            # and follow the href to dump the details of all children
            print crc.perform_get(child["href"])


