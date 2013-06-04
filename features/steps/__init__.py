#!/usr/bin/env python 

###########################################################################
# Author: Jon Kelley <jon.kelley@rackspace>                               #
# Date: May 12 2013                                                       #
# Title:  Testvapi. TestvalueAPI. It tests the values and stuff.          #
# Purpose:                                                                #
#        This nifty program lets you unittest any API using restful       #
#        Gherkin style language syntax. It has optional hooks for greylog.#
#        It's the ultimate ops/QE testing tool ever for restful API's.    #
#                                                                         #
#        Find examples, source, instructions on github.                   #
#             https://github.com/jonkelleyatrackspace/testvapi            #
# Python Version: 2.7.3 ###################################################
#  Dependecies:         # The dude abides. 
#    behave  1.2.2      #
#    requests 1.2.0     #
#    jsonpath 0.54      #
#########################
########################################################################
# Test Settings
#-----------------------------------------------------------------------
# Graylog  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
graylog_servers = { 'x' : '127.0.0.1', 'y' : '127.0.0.2' } 
# Either set to false for disable, or set to a dictionary like { 'desc' : '0.0.0.0' , }
                                        
graylog_facility    = 'GELFtv'  # Your graylog faculity

# Requests options %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
verify_ssl_certificates    = False          # If your SSL certs are bad
                                            # you will get nasty exceptions.
                                            # You should have good SSL certs.
                                            # If you don't, set this to False.
                                            # Then fix your certs.
                                            # Then set this to true.
########################################################################
 
#########################################################################
# Giant wall of importation devices.                                    #
#########################################################################
from behave import *                                                    # =>  Behave makes sure the API's behave, man.
import requests                                                         # =>  <3
from urlparse import urljoin                                            # =>  Allows url manipulation.
from urlparse import urlparse                                           # =>  For greylog gethostname byurl
import logging; logging.basicConfig(level=logging.CRITICAL)             # =>  Only make CRIT filtered to stdout
import json                                                             # =>  We use this.
import traceback                                                        # =>  traceback.format_exc()!
import time                                                             # =>  For request time benchmarking.
from socket import *; import zlib                                       # =>  For the graylogclient class.
                                                                        # => and for banner fetcher
import os # for open()
import urllib2; u = urllib2.urlopen('http://checkip.dyndns.org'); line = u.next(); LOCAL_IP=line.split("<")[6].split().pop()
#########################################################################

class ansi:
    """ Cheap hax to get some ANSI colors in my life """
    HEADER = '\033[95m';  OKBLUE = '\033[94m'; OKGREEN = '\033[92m'
    WARNING = '\033[93m'; FAIL   = '\033[91m' ;ENDC    = '\033[0m'

if not graylog_servers:
    """ THX STYLE INTRO """
    logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi :: Testing the values of all your apis          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::    while you relax                           " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::       on the top some mountains              " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::    with a bottle of scotch                   " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::          and laserbeams and greylog          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi :: on your android phone and stuff.             " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::                well                          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::                      almost anyway.          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "AUTHOR   :: Jon.Kelley@rackspace                         " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO

def get_status_code(status):
    try:
        return int(status)
    except TypeError:
        # Trick to accept status strings like 'not_found', as well.
        return getattr(requests.codes, status)

class graylogclient():
    """ Assuming you did from socket import *; import zlib
        So this little classy thing lets you send off UDP data to your graylog server.
        If the host doesn't exist, no biggie, udp doesnt care!
    """
    def log(self, message, server='localhost', port=12201, maxChunkSize=8154):
            graylog2_server = server
            graylog2_port = port
            maxChunkSize = maxChunkSize

            UDPSock = socket(AF_INET,SOCK_DGRAM)
            zmessage = zlib.compress(message)
            UDPSock.sendto(zmessage,(graylog2_server,graylog2_port))
            UDPSock.close()

def tcpbanner(targetHost, targetPort, timeOut):
    """ from socket import *
        Crafty way to retrieve socket banneers . up to a whole 100 bytes!!@96 
        >> tcpbanner(target_host, target_port)
        
        No exception wrapper, do it on your end!!
        """

    connsocket = socket(AF_INET, SOCK_STREAM)
    connsocket.settimeout(timeOut)
    connsocket.connect((targetHost, targetPort))
    connsocket.send('Hi there\r\n')
    results = connsocket.recv(100)
    print 'OUR PAYLOAD IS EQUAL TO: ' + str(results)
    connsocket.close()

class YourTestWasFatalException(Exception):
	def __init__(self, ivalue):
		#Exception.__init__( self, ivalue )  # Uncomment this to add class into trcbck.
		self.value = ivalue
		#print "ERRORs have been found.  Find the Traceback for details."
	def __str__(self):
		return " >-->  : " + self.value

def testoutcome(isokay=None,metrics={}):
    if isokay == None:
        raise Exception("The result should always be either isokay True|False")

    if metrics['_testtype'] == 'http':
        print('HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG')
        print('>>>> Request Data <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(metrics['_httprequest'])
        print('>>>> Response Head <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(metrics['_httpresponsehead'])
        print('>>>> Response <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(metrics['_httpresponse'])
        print('END.HTTP.DEBUG....END.HTTP.DEBUG....END.HTTP.DEBUG....END.HTTP.DEB')

    try:
        # Attempt to rewrite all auth tokens into obscurity.
        for (header,value) in metrics['_httprequesthead'].items():
            #print "wildxthang " + str(header + value)
            if header.lower() == 'x-auth-token':
                metrics['_httprequesthead'][header] = '***CENSORED***'
    except NameError:
        pass

    if graylog_servers:
        message = {}
        message['version']                  = '1.0'
        # 0=emerg,
        # 1=alert, 
        # 2=crit,
        # 3=err,
        # 4=warning,
        # 5=notice,
        # 6=info,
        # 7=debug
        if isokay:
            message['level']                = '6'
        else:
            message['level']                = '3'

        message['facility']                 = graylog_facility
        
        try:
            message['host'] = metrics['_targethost']
        except NameError:
            message['host'] = 'unknown'

        gherkinstep = str(metrics['_thestep'])
        if isokay:
            message['short_message']   = "OKAY"
            message['short_message']   += " step_" + gherkinstep.replace(" ", "_")
        else:
            message['short_message']   = "FAIL" 
            message['short_message']   += " step_" + gherkinstep.replace(" ", "_")

        for key,value in metrics.items():
            # Send all metrics accumulated thus far over to graylog.
            message[key] = str(value)
            #print "......." + key + " -> " + str(value)

        try:
            print message
            gelfinstance = graylogclient()
            for k,v in graylog_servers.items():
                gelfinstance.log(json.dumps(message),v) # writeout
        except Exception, e:
            print("Graylog send request error. EXCEPTION: " + str(e))

    # Hook em
    if not isokay:
        try:
            raise RuntimeError(metrics['_exception'])
        except NameError:
            raise YourTestWasFatalException("Test failed without an _exception metric. Tests should always raise on failure.")

def curlcmd(verb='',url='',timeout='30',reqheaders=[{}],payload=None,verify=True):
    """ This builds curl commands, for the devops engineer who wants proof.
    e.g.:
    >> curlcmd(verb='GET',url='http://aol.com',timeout=10,payload=None,sslverify=False)
    >> curlcmd(verb='POST',url='http://aol.com',timeout=10,payload="TEST",sslverify=True)

    There's lots TODO and add im sure.
    """
    timeout=str(int(timeout))
    curlcmd =  'curl -v '
    curlcmd += ' -X'+verb+' '
    curlcmd += ' --connect-timeout ' + timeout + ' '
    if verify == False:
        curlcmd += ' --insecure '
    try:
        # Attempt to rewrite all auth tokens into obscurity.
        for (header,value) in reqheaders.items():
            #print "wildxthang " + str(header + value)
            if header.lower() == 'x-auth-token': value = '***CENSORED FOR GREAT JUSTICE ***'
            curlcmd += "-H " + "\'" + header + ": " + value + "\' "
    except AttributeError:
        pass
    if payload:
        curlcmd += "--data-ascii \'" + payload + "\' " 
    curlcmd += "\'"+url+"\'"
    return str(curlcmd)
