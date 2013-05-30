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
graylog_server      = '127.0.0.1'       # If this was a string 
                                            # to a graylog server all your messages 
                                            # would magically go there.
                                            # Else False is disabled.
                                        
graylog_facility    = 'valkyrietest.GELF'  # Your graylog faculity

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
#########################################################################

class ansi:
    """ Cheap hax to get some ANSI colors in my life """
    HEADER = '\033[95m';  OKBLUE = '\033[94m'; OKGREEN = '\033[92m'
    WARNING = '\033[93m'; FAIL   = '\033[91m' ;ENDC    = '\033[0m'

if not graylog_server:
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
    print '' + str(results)
    connsocket.close()

def assertionthing(**kwargs):
    """ This is a giant event processor thing.
        I'll clean it up and break it out later I promise.
        
        Any event it basically evaluates based on if it's FAIL or not, and then
        aggregates and collects the data from the entire unit test from kwargs.
        
        If run from the TTY it's also what throws the assertion failures that you
        see on your console.
        
        It also hooks greylog in this area to funnel all your datas to the internets
        in the event you have an IP configured instead of false.
    """
    statuscode     = kwargs.get('statuscode',None)
    latency     = kwargs.get('latency',None)
    latency     = "%.*f" % ( 3, latency ) # Strip off all but 3 char
    gherkinstep     = kwargs.get('gherkinstep',None)
    if kwargs.get('success',False) == True:
        _success = True # If successful, we change greylogs err level
    else:
        _success = False
    verb            = kwargs.get('verb',None)               # VeRB USED
    requesturl      = kwargs.get('requesturl',None)         # REQUEST URL
    requestpath     = urlparse(requesturl).path
    host            = urlparse(requesturl).netloc.split(":")[0] # Gets just hostname
    requesthead     = kwargs.get('requesthead',None)        # REQUEST HEADERS
    request         = kwargs.get('request',None)            # REQUEST 
    responsehead    = kwargs.get('responsehead',None)       # RESPONSE HEADERS
    response        = kwargs.get('response',None)           # HTTP RAW RESPONSE
    curlcommand          = kwargs.get('curlcommand',None)             # The reason we failed humanly aka RCA
    logic           = kwargs.get('logic',None)              # The logic why we failed 'parse error'

    # Logs some useful debugging data to stdout for QE
    print('HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG')
    print('>>>> Request Head for (' + verb + " " + host + ') <<<<')
    print(requesthead)
    print('>>>> Request Data <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(request)
    print('>>>> Response Head <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(responsehead)
    print('>>>> Response <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(response)
    print('END.HTTP.DEBUG....END.HTTP.DEBUG....END.HTTP.DEBUG....END.HTTP.DEB')

    # Logs the magical and wonderful outputs to graylog for OPS.
    if graylog_server:
        message = {}
        message['version']      = '1.0'
        # Level:            DEC .............. Syslog level (0=emerg, 1=alert, 2=crit, 3=err, 4=warning, 5=notice, 6=info, 7=debug)
        if _success:    message['level']            = '6'
        else:           message['level']            = '3'
        message['facility']                         = graylog_facility
        message['host']                             = str(host)
        if _success:
            message['short_message']    = "OKAY " + str(requestpath)
            message['short_message']   += " STAUS" + str(statuscode)
            message['short_message']   += " VERB" + str(verb)
            gherkinstep = str(gherkinstep)
            message['short_message']   += " STEP" + gherkinstep.replace(" ", "_")
        else:
            message['short_message']    = "FAIL " + str(requestpath)
            message['short_message']   += " STATUS" + str(statuscode)
            message['short_message']   += " VERB" + str(verb)
            gherkinstep = str(gherkinstep)
            message['short_message']   += " STEP" + gherkinstep.replace(" ", "_")

        message['full_message'] = '=======Request=======\n' + str(request) + '\n\n\n=======Response=======\n' + 'Headers:\n' + str(responsehead) + '\n\nBody:\n' + str(response)
        message['testrequirements']         = str(gherkinstep)
        message['reproducecommand']              = str(curlcommand)
        message['testoutcome']              = str(logic)
        message['httpverb']                 = str(verb)
        message['httpcode']                 = str(statuscode)
        if latency != '-1.000': # Hack, you can inseert -1000 to omit this field.
            message['httplatency']          = str(latency)
        message['fullurl']                  = str(requesturl)
        message['requrl']                   = str(requestpath)
        print message
        try:
            gelfinstance = graylogclient()
            gelfinstance.log(json.dumps(message),graylog_server) # writeout 
        except:
            print("Graylog send request error. I don't know why!!!!")

    # Raise typical unit testing exception.
    if not _success:
        raise AssertionError(ansi.OKBLUE + "\nRESOURCE .......: " + ansi.FAIL + str(requesturl)   + 
                             ansi.OKBLUE + "\nREPRODUCE WITH..: " + ansi.FAIL + str(curlcommand) +
                             ansi.OKBLUE + "\nUNDERLYING_LOGIC: " + ansi.FAIL + str(logic)  + ansi.ENDC)

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
        ## If headers exist this will work.
        for (header,value) in reqheaders.items():
            print header,value
            if header == 'x-auth-token': value = '***CENSORED FOR YOU KNOW SAFETY***'
            curlcmd += "-H " + "\'" + header + ": " + value + "\' "
    except AttributeError:
        pass
    if payload:
        curlcmd += "--data-ascii \'" + payload + "\' " 
    curlcmd += "\'"+url+"\'"
    return str(curlcmd)
