from juno import *

@get('/')
def index(web):
    append('Location: %s      <br />' % web.location)
    append('Full Location: %s <br />' % web.full_location)
    append('User Agent: %s    <br />' % web.user_agent)

run()
