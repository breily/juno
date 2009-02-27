from juno import *

init({'middleware': [('paste.gzipper.middleware', {'compress_level': 1})]})

@route('/')
def index(web):
    return 'Hello World!'

if __name__ == '__main__':
    run()
