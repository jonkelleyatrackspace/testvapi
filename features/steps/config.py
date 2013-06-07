#!/usr/bin/env python

# Graylog.Server.
#  This can be used to store great data about the operation of your API when tests are run.
#  You can add as many servers as you want.
#  Examples:
#       DISABLE:         graylog_servers = False
#       ONE SERVER :     graylog_servers = { 'graylog' : '127.0.0.1'} 
#       TWO SERVERs:     graylog_servers = { 'graylog' : '127.0.0.1', 'graylog-failover' : '192.168.0.1', } 
graylog_servers = False 

# Graylog.Facility
#  Graylog docs suggest 'GELF' for gelf applications, syslog for syslog sources, etc.      
graylog_facility    = 'GELFtv'  # Your graylog faculity


# Requests.SSL.Verification
#  Do we care if the cert is expired, doesnt match common name, or some other problem?
#   Set this to TRUE if it's true.
VERIFY_SSL = False

