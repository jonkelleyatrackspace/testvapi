#############################
## GIVEN
#############################
@given('my request has the auth token "{token}"')                       #feature-complee
def step(context, token):
    """ Shunt style Add x-auth-header for token automagically """
    context.execute_steps(unicode("Given my request has the header \"x-auth-token\" with the value \"{token}\"".format(token=token)))

@given('my request has the header "{header}" with the value "{value}"') #feature-complee
def step(context, header, value):
    context.request_headers[header] = value

@given('my request endpoint is "{endpoint}"')                           #feature-complee
def step(context, endpoint):
    """ This is where you want to define what python.requests should connect to.
        You know, think:
                        my request endpoint is "https://myendpoint.local:30000"
                        my request endpoint is "http://127.0.0.1"
    """
    context.request_endpoint = endpoint

@given('my request has a timeout of {seconds} seconds')                 #feature-complee
def step(context, seconds):
    """ This is where you want to define how long is TOO LONG for the server to responde to your requests.
        This should throw a red flag if the API is problematic.
        You know, think:
                        my request endpoint is "https://myendpoint.local:30000"
                        my request endpoint is "http://127.0.0.1"
    """
    context.request_timeout = float(seconds)

#############################
## WHEN
#############################
@when('I connect to {host} on port {port} then it must respond within {timeout} seconds')
@when('I connect to {host} on port {port} then it must respond within {timeout} second')
def step(context,host,port,timeout):
    stepsyntax='I connect to {host} on port {port} then it must respond within {timeout} seconds'.format(host=host,port=port,timeout=timeout)
    # Below is a horrible hack to get the hostnames for endpoints to be targetted.
    #  a redesign is immenent.
    hostname = str(getfqdn()) # getfdqn() will lookup the localname, then set it to the value of PTR if its there
                         # if it differs.
                         # on the otherhand gethostname() always pulls the localname, no reverse lookups

    # Opslove.
    curlcommand = 'telnet ' + str(host) + ' ' + str(int(port))

    try:
        port = int(port)
        timeout = float(timeout)

        before          = time.time()
        datagrams_ahoy  = tcpbanner(host,port,timeout)
        after           = time.time()
        latency         = after - before
        
        # All metrics prepending with _ get sent to graylog as metric.
        testmetrics = { '_targethost'             : hostname,             # Remote test
                        '_originhost'             : LOCAL_IP,             # Test source
                        '_thecmd'                 : curlcommand,
                        '_thestep'                : stepsyntax,
                        '_latency'                : latency,
                        '_testtype'               : 'socket'
                        }
        testoutcome(isokay=True, metrics=testmetrics)
    except:
        failure_logic = "SocketError " +str(traceback.format_exc())
        testmetrics = { '_targethost'             : hostname,
                        '_originhost'             : LOCAL_IP,
                        '_thecmd'                 : curlcommand,   # Reproduce one liner.
                        'full_message'            : str(traceback.format_exc()),
                        '_exception'              : str(traceback.format_exc()),
                        '_thestep'                : stepsyntax,
                        '_latency'                : '30',
                        '_testtype'               : 'socket',
                        }
        testoutcome(isokay=False, metrics=testmetrics)


@when('I get "{path}"')
def step(context, path):
    """ Sends GET verb to path
        EXAMPLE: I get "cloud_account/9363835"
    """
    verb = "GET"
    stepsyntax = "I " + verb + " {path}".format(path=path)

    context.requestpath = path
    requesturl  = urljoin(context.request_endpoint, path)   #i.e. https://localhost:3000/v1/operation
    requestpath = path                                      #i.e. /v1/operation
    requesthost = urlparse(requesturl).netloc.split(":")[0] #i.e. localhost

    try:                timeout = int(context.request_timeout)
    except NameError:   timeout = 30

    # Ops yay
    thiscmd = curlcmd(verb=verb,url=requesturl,timeout=timeout,reqheaders=context.request_headers,payload=None,verify=VERIFY_SSL)

    testmetrics = {}
    testmetrics['_targethost']  = requesthost
    testmetrics['_requestpath'] = requestpath
    testmetrics['_requesturl']  = requesturl
    testmetrics['_testcamefrom'] = LOCAL_IP
    testmetrics['_thecmd']      = thiscmd
    testmetrics['_httpverb']    = verb
    testmetrics['_testtype']    = 'http'
    testmetrics['_thestep']     = stepsyntax

    if VERIFY_SSL:
        testmetrics['_sslcertverify'] = 'True'
    else:
        testmetrics['_sslcertverify'] = 'False'

    try:
        before              = time.time()
        context.response    = requests.get(requesturl, timeout=timeout,headers=context.request_headers,verify=VERIFY_SSL) # Makes full response.
        after               = time.time()
        latency             = after - before
        
        try:                 httpstatus          = str(context.response.status_code)
        except AttributeError:   httpstatus          = str(0)
        try:                httprequesthead     = context.request_headers
        except NameError:   httprequesthead     = {}
        try:                httprequest         = str(payload)
        except NameError:   httprequest         = None
        try:                httpresponsehead    = context.response.headers
        except NameError:   httpresponsehead    = {}
        try:                httpresponse        = str(context.response.text)
        except NameError:   httpresponse        = None
        testmetrics['_httprequesthead']     = httprequesthead
        testmetrics['_httprequest']         = httprequest
        testmetrics['_httpresponse']        = httpresponse
        testmetrics['_httpresponsehead']    = httpresponsehead
        testmetrics['full_message']         = '\n========request========\n' + str(httprequest) + '\n\n\n========resp.headers========\n' + str(httpresponsehead) + '\n\n\n========response========\n' + str(httpresponse)
        testmetrics['_httpstatuscode']      = httpstatus
        testmetrics['_latency']             = latency

        context.httpstate = testmetrics
    except:
        try:                httprequesthead     = context.request_headers
        except NameError:   httprequesthead     = {}
        try:                httprequest         = str(payload)
        except NameError:   httprequest         = None
        try:                httpresponsehead    = context.response.headers
        except NameError:   httpresponsehead    = {}
        httpresponsehead    = {}
        httpresponse        = None
        httpstatus          = '0'
        
        testmetrics['_httprequesthead']     = httprequesthead
        testmetrics['_httprequest']         = httprequest
        testmetrics['_httpresponse']        = httpresponse
        testmetrics['_httpresponsehead']    = httpresponsehead
        testmetrics['full_message']         = 'HTTP.Requests.Exception:' +  str(traceback.format_exc())
        testmetrics['_httpstatuscode']      = httpstatus
        testmetrics['_latency']             = timeout
        testmetrics['_exception']           = str(traceback.format_exc()) # For exceptions!

        context.httpstate = testmetrics
        testoutcome(isokay=False, metrics=testmetrics)


#TODO @when('I post "{path}" payload file "{payload}"')    

@when('I post "{path}" with the data from file "{filename}"')                        # feature-complete
@when('I post "{path}" with the docstring below')                        # feature-complete
def step(context, path,filename=None):
    try:
        payload = context.text # This is what captures the docstring as payload
    except AttributeError: #It just means docstring wasnt used in this case.
        payload = open(filename, "rb").readlines()[0]
    
    verb = "POST"
    stepsyntax = "I " + verb + " {path}".format(path=path)

    context.requestpath = path
    requesturl  = urljoin(context.request_endpoint, path)   #i.e. https://localhost:3000/v1/operation
    requestpath = path                                      #i.e. /v1/operation
    requesthost = urlparse(requesturl).netloc.split(":")[0] #i.e. localhost

    try:                timeout = int(context.request_timeout)
    except NameError:   timeout = 30

    # Ops yay
    thiscmd = curlcmd(verb=verb,url=requesturl,timeout=timeout,reqheaders=context.request_headers,payload=None,verify=VERIFY_SSL)

    testmetrics = {}
    testmetrics['_targethost']  = requesthost
    testmetrics['_requestpath'] = requestpath
    testmetrics['_requesturl']  = requesturl
    testmetrics['_testcamefrom'] = LOCAL_IP
    testmetrics['_thecmd']      = thiscmd
    testmetrics['_httpverb']    = verb
    testmetrics['_testtype']    = 'http'
    testmetrics['_thestep']     = stepsyntax

    if VERIFY_SSL:
        testmetrics['_sslcertverify'] = 'True'
    else:
        testmetrics['_sslcertverify'] = 'False'

    try:
        before              = time.time()
        context.response = requests.post(requesturl, data=payload,timeout=timeout,headers=context.request_headers,verify=False) # Makes full 
        after               = time.time()
        latency             = after - before
        
        try:                 httpstatus          = str(context.response.status_code)
        except AttributeError:   httpstatus          = str(0)
        try:                httprequesthead     = context.request_headers
        except NameError:   httprequesthead     = {}
        try:                httprequest         = str(payload)
        except NameError:   httprequest         = None
        try:                httpresponsehead    = context.response.headers
        except NameError:   httpresponsehead    = {}
        try:                httpresponse        = str(context.response.text)
        except NameError:   httpresponse        = None
        testmetrics['_httprequesthead']     = httprequesthead
        testmetrics['_httprequest']         = httprequest
        testmetrics['_httpresponse']        = httpresponse
        testmetrics['_httpresponsehead']    = httpresponsehead
        testmetrics['full_message']         = '\n========request========\n' + str(httprequest) + '\n\n\n========resp.headers========\n' + str(httpresponsehead) + '\n\n\n========response========\n' + str(httpresponse)
        testmetrics['_httpstatuscode']      = httpstatus
        testmetrics['_latency']             = latency

        context.httpstate = testmetrics
    except:

        try:                httprequesthead     = context.request_headers
        except AttributeError:   httprequesthead     = {}
        try:                httprequest         = str(payload)
        except AttributeError:   httprequest         = None
        httpresponsehead    = {}
        httpresponse        = None
        httpstatus          = '0'

        testmetrics['_httprequesthead']     = httprequesthead
        testmetrics['_httprequest']         = httprequest
        testmetrics['_httpresponse']        = httpresponse
        testmetrics['_httpresponsehead']    = httpresponsehead
        testmetrics['full_message']         = 'HTTP.Requests.Exception:' +  str(traceback.format_exc())
        testmetrics['_httpstatuscode']      = httpstatus
        testmetrics['_latency']             = timeout
        testmetrics['_exception']           = str(traceback.format_exc()) # For exceptions!

        context.httpstate = testmetrics
        testoutcome(isokay=False, metrics=testmetrics)
    
#@when('I delete "{path}"')                                              # TODO untested XXX
#def step(context, path):# XXX UNTESTED XXX
#    """ Entirely untested!! (no unit tests written for this yet)
#        Sends DELETE verb to path
#        EXAMPLE: I delete "server/entity/id/9363835"
#    """
#    stepsyntax = "I DELETE {path}".format(path=path)
#    url = urljoin(context.request_endpoint, path)
#    try: # There's got to be a better way to set None if missing/attributerror
#        timeout = context.request_timeout
#    except AttributeError:
#        timeout = None
#    timebench_before = time.time()
#    context.response = requests.delete(url,timeout=timeout,headers=context.request_headers) # Makes full response.
#    timebench_after = time.time()
#    
#    _latency = timebench_after - timebench_before
#    try:    _statuscode         = str(context.response.status_code)
#    except: _statuscode         = '-1'
#    try:    _requestheaders     = str(context.request_headers)
#    except: _requestheaders     = None
#    try:    _request            = str(payload)
#    except: _request            = None
#    try:    _responseheaders    = str(context.response.headers)
#    except: _responseheaders    = None
#    try:    _response            = str(context.response.text)
#    except: _response            = "Not applicable (No data?)" 
#    context.httpstate = { 'requesturi'      : url ,
#                            'verb'            : 'GET' ,
#                            'requestheaders'  : _requestheaders ,
#                            'request'         : _request ,
#                            'responseheaders' : _responseheaders ,
#                            'response'        : _response ,
#                            'latency'         : _latency,
#                            'statuscode'      : _statuscode
#                        }

#TODO @when('I put "{path}" payload file "{payload}"')  
@when('I put "{path}" with payload "{payload}"')                        # TODO untested XXX
def step(context, path,payload):
    """ Entirely and completely untested """
    stepsyntax = "I put {path}".format(path=path)
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None
    timebench_before = time.time()
    context.response = requests.put(url, data=payload,timeout=timeout,headers=context.request_headers) # Makes full response.
    timebench_after = time.time()
    
    _latency = timebench_after - timebench_before
    try:    _statuscode         = str(context.response.status_code)
    except: _statuscode         = '-1'
    try:    _requestheaders     = str(context.request_headers)
    except: _requestheaders     = None
    try:    _request            = str(payload)
    except: _request            = None
    try:    _responseheaders    = str(context.response.headers)
    except: _responseheaders    = None
    try:    _response            = str(context.response.text)
    except: _response            = "Not applicable (No data?)" 
    context.httpstate = { 'requesturi'      : url ,
                            'verb'            : 'GET' ,
                            'requestheaders'  : _requestheaders ,
                            'request'         : _request ,
                            'responseheaders' : _responseheaders ,
                            'response'        : _response ,
                            'latency'         : _latency,
                            'statuscode'      : _statuscode
                        }

# TODO @when('I post "{path}" with multipart payload "{payload}"')      TODO 


#############################
## THEN
#############################
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will contain string "{text}"')
def step(context, text):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will contain string {text}".format(text=text)

    if text not in context.response.text:
        try:
            raise YourTestWasFatalException('Unexpected string')
        except:
            testmetrics['_exception'] = str(traceback.format_exc())
            testoutcome(isokay=False, metrics=testmetrics)
    else:
        testoutcome(isokay=True, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will not contain string "{text}"')
def step(context, text):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will not contain string {text}".format(text=text)

    if text in context.response.text:
        try:
            raise YourTestWasFatalException('Unexpected string')
        except:
            testmetrics['_exception'] = str(traceback.format_exc())
            testoutcome(isokay=False, metrics=testmetrics)
    else:
        testoutcome(isokay=True, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will have the header "{header}" with the value "{value}"')
def step(context, header, value):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] != value:
        try:
            raise YourTestWasFatalException('Unexpected headers')
        except:
            testmetrics['_exception'] = str(traceback.format_exc())
            testoutcome(isokay=False, metrics=testmetrics)
    else:
        testoutcome(isokay=True, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will have the header "{header}"')
def step(context, header):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will have the header {header}".format(header=header)
    if header not in context.response.headers.keys():
#        logging.debug("I saw these headers though...")
#        for k, v in context.response.headers.iteritems():
#            logging.debug("header: " + k + " => " + v)
        try:
            raise YourTestWasFatalException('Unexpected headers')
        except:
            testmetrics['_exception'] = str(traceback.format_exc())
            testoutcome(isokay=False, metrics=testmetrics)
    else:
        testoutcome(isokay=True, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will not have the header "{header}" with the value "{value}"')
def step(context, header, value):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will not have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] == value:
        try:
            raise YourTestWasFatalException('Unexpected headers')
        except:
            testmetrics['_exception'] = str(traceback.format_exc())
            testoutcome(isokay=False, metrics=testmetrics)
    else:
        testoutcome(isokay=True, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will not have the header "{header}"')
def step(context, header,reason):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will not have the header {header}".format(header=header)
    if context.response.headers[header]:
        try:
            raise YourTestWasFatalException('Unexpected headers')
        except:
            testmetrics['_exception'] = str(traceback.format_exc())
            testoutcome(isokay=False, metrics=testmetrics)
    else:
        testoutcome(isokay=True, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response json will have path "{path}" with value "{value}" as "{valuetype}"')
def step(context, path, value, valuetype):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response json will have the path {path} with value {value} as {valuetype}".format(path=path,value=value,valuetype=valuetype)
    # Check path exists 
    try:
        if not context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists first of all... else raise() """
            try:
                raise YourTestWasFatalException('Response json has unexpected path')
            except:
                testmetrics['_exception'] = str(traceback.format_exc())
                testoutcome(isokay=False, metrics=testmetrics)

        # Effing unicode strings need hacks to determine their type.
        if valuetype == "int":
            value = int(value)
        elif valuetype == "str":
            value = str(value)
        elif valuetype == "unicode":
            value = unicode(value)
        elif valuetype == "bool" or valuetype == "boolean":
            if value == "true" or value == "True":
                value = True
            else:
                value=False
        # Check if value is there as desired.
        if not value in context.jsonsearch.returnpath(context.response.json(),path):
            """ Verify if value within returned list of results for that path.. else raise() """
            try:
                raise YourTestWasFatalException('Response json has unexpected path')
            except:
                testmetrics['_exception'] = str(traceback.format_exc())
                testoutcome(isokay=False, metrics=testmetrics)
        else:
            testoutcome(isokay=True, metrics=testmetrics)
    except:
        testmetrics['_exception'] = str(traceback.format_exc())
        testoutcome(isokay=False, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response json will not have path "{path}" with value "{value}" as "{valuetype}"')
def step(context, path, value, valuetype):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response json will not have the path {path} with value {value} as {valuetype}".format(path=path,value=value,valuetype=valuetype)
    # If path even exists..
    try:
        if context.jsonsearch.pathexists(context.response.json(),path):
            # Effing unicode strings need hacks to determine their type.
            if valuetype == "int":
                value = int(value)
            elif valuetype == "str":
                value = str(value)
            elif valuetype == "unicode":
                value = unicode(value)
            elif valuetype == "bool" or valuetype == "boolean":
                if value == "true" or value == "True":
                    value = True
                else:
                    value=False

            if value in context.jsonsearch.returnpath(context.response.json(),path):
                """ Verify if string is within path, if so raise() """
                try:
                    raise YourTestWasFatalException('Response json has unexpected path')
                except:
                    testmetrics['_exception'] = str(traceback.format_exc())
                    testoutcome(isokay=False, metrics=testmetrics)
            else:
                testoutcome(isokay=True, metrics=testmetrics)
    except:
        testmetrics['_exception'] = str(traceback.format_exc())
        testoutcome(isokay=False, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response json will have path "{path}"')
def step(context, path):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response json will have path {path}".format(path=path)
    #raise Exception(context.response.json())
    try:
        if not context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists first of all """
            try:
                raise YourTestWasFatalException('Response json has unexpected path')
            except:
                testmetrics['_exception'] = str(traceback.format_exc())
                testoutcome(isokay=False, metrics=testmetrics)
        else:
            testoutcome(isokay=True, metrics=testmetrics)
    except:
        testmetrics['_exception'] = str(traceback.format_exc())
        testoutcome(isokay=False, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response json will not have path "{path}"')
def step(context, path):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response json will not have path {path}".format(path=path)
    try:
        if context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists , then fail """
            try:
                raise YourTestWasFatalException('Response json has unexpected path')
            except:
                testmetrics['_exception'] = str(traceback.format_exc())
                testoutcome(isokay=False, metrics=testmetrics)
        else:
            testoutcome(isokay=True, metrics=testmetrics)
    except:
        testmetrics['_exception'] = str(traceback.format_exc())
        testoutcome(isokay=False, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will have status {status}')
def step(context, status):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will have status {status}".format(status=status)
    try:
        status = get_status_code(status)
        if context.response.status_code != status:
            try:
                raise YourTestWasFatalException('Response status not expected')
            except:
                testmetrics['_exception'] = str(traceback.format_exc())
                testoutcome(isokay=False, metrics=testmetrics)
        else:
            testoutcome(isokay=True, metrics=testmetrics)
    except:
        testmetrics['_exception'] = str(traceback.format_exc())
        testoutcome(isokay=False, metrics=testmetrics)
# ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ---- ----  ----
@then('the response will not have status {status}')
def step(context, status):
    testmetrics                 = context.httpstate
    testmetrics['_thestep']     = "the response will not have status {status}".format(status=status)
    try:
        status = get_status_code(status)
        if context.response.status_code == status:
            try:
                raise YourTestWasFatalException('Response status not expected')
            except:
                testmetrics['_exception'] = str(traceback.format_exc())
                testoutcome(isokay=False, metrics=testmetrics)
        else:
            testoutcome(isokay=True, metrics=testmetrics)
    except:
        testmetrics['_exception'] = str(traceback.format_exc())
        testoutcome(isokay=False, metrics=testmetrics)

