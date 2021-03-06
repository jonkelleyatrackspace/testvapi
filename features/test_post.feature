Feature: Tests the identity system with a bogus API key and makes sure the
	system replies with unauthorized.

  Scenario Outline: Make sure status page returns!!
    Given my request has the header "content-type" with the value "application/json"
    Given my request endpoint is "<myendpoints>"
    Given my request has a timeout of 10 seconds
    When I post "/v2.0/tokens" with the docstring below
		"""
		{ "auth": { "RAX-KSKEY:apiKeyCredentials": { "username": "hi", "apiKey": "bogus" }}}
		"""
    Then the response json will have path "$.unauthorized"
    Then the response json will have path "$.unauthorized.code" with value "401" as "int"
    Then the response json will have path "$.unauthorized.message" with value "Username or api key is invalid" as "str"
    Then the response will have status 401
  Examples:
  | myendpoints |
  | https://identity.api.rackspacecloud.com |


  Scenario Outline: Make sure status page returns!!
    Given my request has the header "content-type" with the value "application/json"
    Given my request endpoint is "<myendpoints>"
    Given my request has a timeout of 10 seconds
    When I post "/v2.0/tokens" with the data from file "/tmp/x"
    Then the response json will have path "$.unauthorized"
    Then the response json will have path "$.unauthorized.code" with value "401" as "int"
    Then the response json will have path "$.unauthorized.message" with value "Username or api key is invalid" as "str"
    Then the response will have status 401
  Examples:
  | myendpoints |
  | https://identity.api.rackspacecloud.com |
