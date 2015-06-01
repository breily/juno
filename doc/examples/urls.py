from juno import *

@get('/say/*:greet/to/*:name/')
def hello(web, greet, name):
    return '%s, %s' % (greet, name)

# /say/hello/to/brian

run()
