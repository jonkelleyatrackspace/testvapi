

# Givens
@given('I send a socket to {host}')                       #untested
def step(context, host):
    stepsyntax = 'i can connect to {host}'.format(host=host)
    """ Attempt to connect to remote host or endpoint of some kind via TCP. Fail otherwise. """
    context.connecthost = host
    

@given('my request has the auth token "{token}"')                       #feature-complee
def step(context, token):
    """ shunt style Add x-auth-header for token automagically """
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

##################################
# Whens

@when('I connect to {host} on port {port} then it must respond within {timeout} seconds')
@when('I connect to {host} on port {port} then it must respond within {timeout} second')
def step(context,host,port,timeout):
    stepsyntax='I connect to {host} on port {port} then it must respond within {timeout} seconds'.format(host=host,port=port,timeout=timeout)
    failure_logic = 'Port is unavailable'
    # Below is a horrible hack to get the hostnames for endpoints to be targetted.
    #  a redesign is immenent.
    hostname = getfqdn() # getfdqn() will lookup the localname, then set it to the value of PTR if its there
                         # if it differs.
                         # on the otherhand gethostname() always pulls the localname, no reverse lookups
    requesturl = 'SocketOrigin://' + str(hostname)
    try:
        before = time.time()
        port = int(port)
        timeout = float(timeout)
        bannerdata = tcpbanner(host,port,timeout)
        after = time.time()
        latency = after - before

        curlcommand = 'telnet ' + str(host) + ' ' + str(int(port))
        assertionthing(success=True,verb='SOCKET',
                    requesturl=requesturl,
                    requesthead=None,
                    request='Is this port online?',
                    responsehead=None,
                    response=str(bannerdata),
                    curlcommand=curlcommand, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=None,latency=latency)
    except:
        failure_logic = "Socket " +traceback.format_exc()
        curlcommand = 'telnet ' + str(host) + ' ' + str(int(port))
        assertionthing(success=False,verb='SOCKET',
                    requesturl=requesturl,
                    requesthead=None,
                    request='Is this port online?',
                    responsehead=None,
                    response='null',
                    curlcommand=curlcommand, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=None,latency=-1.000,)


@when('I get "{path}"')                                                 #feature-complee
def step(context, path):
    """ Sends GET verb to path
        EXAMPLE: I get "cloud_account/9363835"
    """
    stepsyntax = "I GET {path}".format(path=path)

    context.requestpath = path
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    try:
        timebench_before = time.time()
        context.response = requests.get(url, timeout=timeout,headers=context.request_headers,verify=False) # Makes full response.
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
        
        # Ops curlcommand
        _curlcommand = curlcmd(verb='GET',url=url,timeout=timeout,reqheaders=context.request_headers,payload=None,verify=False)
        print "CURL COMMAND: " + _curlcommand

        context.httpstate = { 'requesturi'      : url ,
                                'verb'            : 'GET' ,
                                'requestheaders'  : _requestheaders ,
                                'request'         : _request ,
                                'responseheaders' : _responseheaders ,
                                'response'        : _response ,
                                'latency'         : _latency,
                                'statuscode'      : _statuscode,
                                'curlcommand'      : _curlcommand
                            }
    except:
        context.httpstate = { 'requesturi'      : url ,
                                'verb'            : 'GET' ,
                                'requestheaders'  : _requestheaders ,
                                'request'         : _request ,
                                'responseheaders' : _responseheaders ,
                                'response'        : _response ,
                                'latency'         : _latency,
                                'statuscode'      : _statuscode,
                                'curlcommand'      : _curlcommand
                            }
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
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
#TODO @when('I post "{path}" payload file "{payload}"')    

@when('I post "{path}" with the data from file "{filename}"')                        # feature-complete
@when('I post "{path}" with the docstring below')                        # feature-complete
def step(context, path,filename=None):
    try:
        payload = context.text # This is what captures the docstring as payload
    except AttributeError: #It just means docstring wasnt used in this case.
        payload = open(filename, "rb").readlines()[0]

    stepsyntax = "I POST {path} with payload below...".format(path=path)
    context.requestpath = path
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    try:
        timebench_before = time.time()
        context.response = requests.post(url, data=payload,timeout=timeout,headers=context.request_headers,verify=False) # Makes full 
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

        _curlcommand = curlcmd(verb='POST',url=url,timeout=timeout,reqheaders=context.request_headers,payload=payload,verify=False)
        print "CURL COMMAND: " + _curlcommand

        context.httpstate = { 'requesturi'      : url ,
                                'verb'            : 'GET' ,
                                'requestheaders'  : _requestheaders ,
                                'request'         : _request ,
                                'responseheaders' : _responseheaders ,
                                'response'        : _response ,
                                'latency'         : _latency,
                                'statuscode'      : _statuscode,
                                'curlcommand'      : _curlcommand
                            }
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    
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

##################################
# Thens
@then('the response will contain string "{text}"')                      # feature-complete
def step(context, text):
    stepsyntax = "the response will contain string {text}".format(text=text)
    failure_logic   = 'Did not find expected text `{text}` in response.'.format(text=text )
    if text not in context.response.text:
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)

@then('the response will not contain string "{text}"')                  # feature-complete
def step(context, text):
    stepsyntax = "the response will not contain string {text}".format(text=text)
    if text in context.response.text:
        failure_logic = 'Found string `{text}` in response.'.format(text=text)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have the header "{header}" with the value "{value}"') # feature-complete
def step(context, header, value):
    stepsyntax = "the response will have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] != value:
        failure_logic = 'HTTP header `{header}` => `{value}` missing in response.'.format(header=header,value=value)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have the header "{header}"')                   # feature-complete
def step(context, header):
    stepsyntax = "the response will have the header {header}".format(header=header)
    if header not in context.response.headers.keys():
#        logging.debug("I saw these headers though...")
#        for k, v in context.response.headers.iteritems():
#            logging.debug("header: " + k + " => " + v)
        failure_logic = 'Missing header `{header}` in response.'.format(header=header) 
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have the header "{header}" with the value "{value}"')# feature-complete
def step(context, header, value):
    stepsyntax = "the response will not have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] == value:
        failure_logic = 'HTTP header `{header}` => `{value}` found in response.'.format(header=header,value=value)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have the header "{header}"')               # feature-complete
def step(context, header,reason):
    stepsyntax = "the response will not have the header {header}".format(header=header)
    if context.response.headers[header]:
        failure_logic = 'HTTP header `{header}` => `{value} found in response.'.format(header=header,value=context.response.headers[header] )
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will have path "{path}" with value "{value}" as "{valuetype}"') # feature-complete
def step(context, path, value, valuetype):
    stepsyntax = "the response json will have the path {path} with value {value} as {valuetype}".format(path=path,value=value,valuetype=valuetype)
    # Check path exists 
    try:
        if not context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists first of all... else raise() """
            failure_logic = 'Response does not have path {path}'.format(path=path)
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)

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
            logging.error(ansi.OKBLUE +  "Gherkin input was " + str(type(value)) + " with value \"" + str(value) + "\" ... remote side contained a list with " + str(context.jsonsearch.returnpath(context.response.json(),path)) + "\n"+ansi.ENDC )
            failure_logic = 'Response json path {path} has no value matching {value}'.format(path=path,value=value)
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will not have path "{path}" with value "{value}" as "{valuetype}"') # feature-complete
def step(context, path, value, valuetype):
    stepsyntax = "the response json will not have the path {path} with value {value} as {valuetype}".format(path=path,value=value,valuetype=valuetype)
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
                logging.error(ansi.OKBLUE +  "Gherkin input was " + str(type(value)) + " with value \"" + str(value) + "\" ... remote side contained a list with " + str(context.jsonsearch.returnpath(context.response.json(),path)) + "\n"+ansi.ENDC )
                failure_logic = 'Response json path {path} has value matching {value}'.format(path=path,value=value)
                assertionthing(success=False,verb=context.httpstate['verb'],
                           requesturl=context.httpstate['requesturi'],
                           requesthead=context.httpstate['requestheaders'],
                           request=context.httpstate['request'],
                           responsehead=context.httpstate['responseheaders'],
                           response=context.httpstate['response'],
                           curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                           logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
            else:
                failure_logic = 'OK'
                assertionthing(success=True,verb=context.httpstate['verb'],
                           requesturl=context.httpstate['requesturi'],
                           requesthead=context.httpstate['requestheaders'],
                           request=context.httpstate['request'],
                           responsehead=context.httpstate['responseheaders'],
                           response=context.httpstate['response'],
                           curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                           logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will have path "{path}"')                      # feature-complete
def step(context, path):
    stepsyntax = "the response json will have path {path}".format(path=path)
    #raise Exception(context.response.json())
    try:
        if not context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists first of all """
            failure_logic = 'Response does not have path {path}'.format(path=path)
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will not have path "{path}"')                  # feature-complete
def step(context, path):
    stepsyntax = "the response json will not have path {path}".format(path=path)
    try:
        if context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists , then fail """
            failure_logic = 'Response json has path {path}'.format(path=path)
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have status {status}')
def step(context, status):
    stepsyntax = "the response will have status {status}".format(status=status)
    try:
        status = get_status_code(status)
        if context.response.status_code != status:
            failure_logic = 'Response status is {response.status_code}, not {status}'.format(response=context.response, status=status)
            assertionthing(sucess=False,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have status {status}')
def step(context, status):
    stepsyntax = "the response will not have status {status}".format(status=status)
    try:
        status = get_status_code(status)
        if context.response.status_code == status:
            failure_logic = 'Response status is {status}'.format(status=status)
            assertionthing(success=False,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    curlcommand=context.httpstate['curlcommand'], gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)

