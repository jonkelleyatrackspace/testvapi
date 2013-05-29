testvapi
========

Tests RESTful API's in Gherkin unit-test stye. Make RESTful QE + OPS testing a breeze with Jenkens!

Requires python 2.7.3 with modules:

`behave  1.2.2`
`requests 1.2.0`
`jsonpath 0.54`
 
Just git clone, then run:

`cd /opt/testvapi`

`pip install behave==1.2.2`

`pip install requests==1.2.0`

`pip install jsonpath==0.5`

Test your install with:

`behave features/identity-frontpage.feature`

Your unit tests will either pass or fail.


If identity is up and it's catalog contains enough healthy elements, this test will pass.
What does testvapi look like when a unittest fails?

Test with:

`behave features/identity-frontpage-failexample.feature`

