from juno import *

@route('/')
def index(web):
    return 'Hello, World'

run()
