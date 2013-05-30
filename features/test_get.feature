Feature: Test the exterior entryway of the Rackspace Public Cloud for general availability
  This is suppose to give you an idea for writing your own templates to check your own API's.
  Good luck!

  Scenario Outline: This is a working example
    Given my request has the header "x-auth-token" with the value "XXXXapikeyXXXX"
    Given my request has the header "jontest" with the value "hi"
    Given my request endpoint is "<myendpoints>"
    Given my request has a timeout of 10 seconds
    When I get "/"
    Then the response json will not have path "$.regression." with value "xxxxx" as "int"
    Then the response json will not have path "$.regressionx."
    Then the response json will have path "$.versions.version[*].status." with value "CURRENT" as "str"
    Then the response will have status 200
  Examples:
  | myendpoints |
  | https://identity.api.rackspacecloud.com:443 |


  Scenario Outline: This test should fail, because it searches for a bad json path
    Given my request has the header "x-auth-token" with the value "XXXXapikeyXXXX"
    Given my request has the header "jontest" with the value "hi"
    Given my request endpoint is "<myendpoints>"
    Given my request has a timeout of 10 seconds
    When I get "/"
    Then the response json will not have path "$.regression." with value "xxxxx" as "int"
    Then the response json will not have path "$.regressionx."
    Then the response json will have path "$.versions.INVALID.PATH.version[*].status." with value "CURRENT" as "str"
    Then the response will have status 200
  Examples:
  | myendpoints |
  | https://identity.api.rackspacecloud.com:443 |
