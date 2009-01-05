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
    if id == 1: return JunoResponse(body="brian reily", status=404)
    # Test 2
    if id == 2: return redirect('/')

# Test 2 and 3
@route('/say/*:greet/to/*:name/')
def hello(web, greet, name):
    return greet + ', ' + name

if __name__ == '__main__':
    # Test 0 
    print "juno: testing sending a string as a response..."
    response = test_request('/test/0/')
    assert response == JunoResponse(body='Hello, World').render()

    # Test 1
    print "juno: testing returning a JunoResponse object..."
    response = test_request('/test/1/')
    assert response == JunoResponse(body="brian reily", status=404).render()

    # Test 2
    print "juno: testing the redirect function..."
    response = test_request('/test/2/')
    j = JunoResponse(status=302)
    j.config['headers'] = { 'Location': '/' }
    assert response == j.render()
    
    # Test 2
    print "juno: testing url wildcards..."
    response = test_request('/say/hi/to/brian/')
    assert response == JunoResponse(body='hi, brian').render()

    # Test 3
    print "juno: testing url wildcards when they are the last parameter..."
    response = test_request('/say/hi/to/brian/reily/')
    assert response == JunoResponse(body='hi, brian/reily').render()

    # Passed
    print '==============================================='
    print 'juno: all tests passed (5 / 5)'
