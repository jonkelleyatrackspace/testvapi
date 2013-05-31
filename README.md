testvapi
========
Testvapi is a small python suite which runs through your API does end-to-end API response verification.

Just because your unit tests all pass != mean the applications external state will meet a particular criteria.

Our goals are simple:

1. Connect to an API from the viewpoint of a customer and run every operation

3. Verify and all facets of an API response.

4. Report all metrics to graylog for ops/qe

Your QE people can test your applications using their console as a reporting tool.
Your OPs people can run these tests from cron or another scheduler and get metrics on API performance 24/7 in graylog.


The best part is, the syntax is so easy you don't have to be a programmer to write your end to end tests.

A limited set of examples showing off lexical syntax:

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

