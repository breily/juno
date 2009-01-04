#
#   Run 'python jtest.py' to test parts of Juno.
#

from juno import *

@route('/test/:id/')
def test(web, id):
    id = int(id)
    # Test 0
    if id == 0: return 'Hello, World'
    # Test 1
    if id == 1: return redirect('/')

@route('/say/*:greet/to/*:name/')
def hello(web, greet, name):
    return greet + ', ' + name

if __name__ == '__main__':
    # Test 0 
    print "juno: testing url routing and string sending..."
    response = test_request('/test/0/')
    assert response == JunoResponse(body='Hello, World').render()

    # Test 1
    print "juno: testing the redirect function..."
    response = test_request('/test/1/')
    j = JunoResponse(status=302)
    j.config['headers'] = { 'Location': '/' }
    assert response == j.render()
    
    # Test 2
    print "juno: testing url wildcards..."
    response = test_request('/say/hi/to/brian/')
    assert response == JunoResponse(body='hi, brian').render()

    # Passed
    print '==============================================='
    print 'juno: all tests passed'
