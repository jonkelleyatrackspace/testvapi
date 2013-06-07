#!/bin/bash -x

# Public github installer.
# Bootstrap your test environment.
# At the end of this procedure you will be able to execute 
#   cd tvapi; tvapi/features/test_get.feature

# When you write some of your tests, why not wrap installation of them in the installer?
#  Go to the testvapi-projectskel, build your unit tests within that tree, then deploy using
#   that projects installer file. It works! I run it from cron for operations 24/7.

# Build testvapi running location.
rm -rfv tvapi
mkdir tvapi

# Inflate the testvapi main codebase in here.
git clone git@github.com:jonkelleyatrackspace/testvapi.git ./tvapi/

# Build virtualenv
# Get dependecies...
virtualenv --no-site-packages tvapi/virtualenv

source tvapi/virtualenv/bin/activate

pip install behave==1.2.2
pip install requests==1.2.0
pip install jsonpath

# Jump into virtualenv
echo -e "\n\n\n====================================\nTestvapi installed.\n See what a simple test that has 1 passing item and 1 failing item looks like."
echo -e "Run:\ncd tvapi; tvapi/features/test_get.feature"


