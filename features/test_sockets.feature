Feature: Maybe testing sockets is important to you.

  Scenario: Test socket addressfailure
    When I connect to aol.com on port 666 then it must respond within 1 seconds
    
  Scenario: Test socket timeout
    When I connect to aol.com on port 666 then it must respond within 1 second

  Scenario: Test socket timeout
    When I connect to aol.com on port 65536 then it must respond within 12 seconds

  Scenario: Test socket timeout
    When I connect to google.com on port 80 then it must respond within 22 seconds

