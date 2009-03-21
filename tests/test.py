# # # # # # # #
#
# When adding features, add some tests for it too.
# Tests are set up so you call a Juno app's URL, it
# does what you need for the test, and then the
# original test function checks the return value.
#
# URL numbers correspond to the order of test cases.
#
# See existing tests.
#
# # # # # # # #

""" ---------------------- """
""" Start Application Code """
""" ---------------------- """

import juno

juno.init({'use_db': False, 'mode': 'wsgi', 'log': False, 'use_static': False, 
           'use_templates': False})

@juno.get('/1/')
def x1(web): return

@juno.get('/2/')
def x2(web): juno.status(404)

@juno.get('/3/')
def x3(web): juno.status(500)

@juno.get('/4/')
def x4(web): return ''.join(''.join([k,v]) for k,v in web.input().items())

@juno.get('/5/')
def x5(web): return str(web.input())

application = juno.run()

""" -------------------------------------- """
""" End Application Code / Start Test Code """
""" -------------------------------------- """

import unittest
from client import Client
client = Client(application)

class ResponseTest(unittest.TestCase):
    """Test basic responses - status codes, headers, bodies. """
    def test200StatusCode(self): 
        """Juno should send a 200 by default"""
        status, _, _ = client.request('/1/')
        self.assertEqual(status, '200 OK')
    def test404StatusCode(self):
        """Juno can use status() to set status code"""
        status, _, _ = client.request('/2/')
        self.assertEqual(status, '404 Not Found')
    def test500StatusCode(self):
        """Juno can use status() to set status code"""
        status, _, _ = client.request('/3/')
        self.assertEqual(status, '500 Internal Server Error')

class QueryStringTest(unittest.TestCase):
    """Test Juno's handling of query strings. """
    def testQueryStringHeader(self):
        """Juno can read query string and echo it back""" 
        _, _, body = client.request('/4/', QUERY_STRING='a=5&b=0')
        self.assertEqual(body, ['a5b0'])
    def testSameQueryStringKeys(self):
        """Juno can handle query strings with multiple indentical keys"""
        _, _, body = client.request('/5/', QUERY_STRING='a=0&a=1')
        self.assertEqual(body, ["{'a': ['0', '1']}"])
    

if __name__ == '__main__':
    unittest.main()
