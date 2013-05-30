testvapi
========
Test Value API script is meant to test your enterprise API for proper responses, headers, data, status codes, latency whatever!

QE people can use this on the command line to get a status output of how many API calls are working or failed
in unit-test style breakdown.

DEVOPS people can set the graylog output to TRUE, then set this up in jenkins, crontab, or whatever to 
do continious testing with performance metrics about the status of your API 24/7.

The best part is, the syntax is so easy you don't have to be a programmer to write unit tests for your API.
Now that's enterprise-easy isn't it!

Here are some examples of its lexical syntax:

	  Scenario Outline: Get accounts
		Given my request has the header "x-auth-token" with the value "xxxx-xxxx-xxxxx"
		Given my request endpoint is "https://api.company.net:443"
		Given my request has a timeout of 10 seconds
		When I get "/get-all-accounts"
		Then the response json will not have path "$.regression." with value "xxxxx" as "int"
		Then the response json will not have path "$.regressionx."
		Then the response json will have path "$.accounts.dfw." with value "account name" as "str"
		Then the response will have status 200


	  Scenario Outline: Make sure login page returns 401 with bogus data
		Given my request has the header "content-type" with the value "application/json"
		Given my request endpoint is "https://identity.api.rackspacecloud.com"
		Given my request has a timeout of 10 seconds
		When I post "/v2.0/tokens" with the docstring below
		            """
		            { "auth": { "RAX-KSKEY:apiKeyCredentials": { "username": "hi", "apiKey": "bogus" }}}
		            """
		Then the response json will have path "$.unauthorized"
		Then the response json will have path "$.unauthorized.code" with value "401" as "int"
		Then the response json will have path "$.unauthorized.message" with value "Username or api key is invalid" as "str"
		Then the response will have status 401

So how do I install it?
-------------

	pip install behave==1.2.2
	pip install requests==1.2.0
	pip install jsonpath==0.5
	git clone git@github.com:jonkelleyatrackspace/testvapi.git
	cd testvapi

How do I send my outputs to graylog?
-------------
Edit `features/steps/steps.py` and change `graylog_server = []` to a list of your hosts.

For example:
		graylog_server = 127.0.0.1

How do I run unit tests?
-------------
Run the example!

	behave features/*.feature
	
You can run the API tests from jenkens, cron etc!!

