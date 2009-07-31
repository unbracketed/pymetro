import unittest
import doctest

from metro import api
from metro.api import initialize_api, MetroAPI

initialize_api()
suite = unittest.TestSuite()

suite.addTest(doctest.DocTestSuite(api))
runner = unittest.TextTestRunner()
runner.run(suite)


#import doctest
#from metro.api import MetroAPI


#TODO

#metroAPI with no param
#metroAPI with string


#make calls with invalid key

